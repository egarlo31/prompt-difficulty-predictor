import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import Mock

from backend.local_llm.ollama_adapter import OllamaAdapter
from modeling.src.data.prompt_io import load_prompts, prompt_id, read_jsonl
from modeling.src.evaluation.batch import CODING_SYSTEM, generate_batch
from modeling.src.evaluation.generate_responses import EvaluationRunner
from modeling.src.sandbox.contracts import SandboxLimits
from modeling.src.sandbox.prepare import extract_python, prepare_sandbox_tasks


class GenerationFlowTests(unittest.TestCase):
    def setUp(self):
        self.client = Mock()
        self.client.generate.return_value.model_dump.return_value = {
            'response': '```python\nprint(1)\n```', 'done': True, 'done_reason': 'stop',
        }
        self.adapter = OllamaAdapter('test', client=self.client, system=CODING_SYSTEM, think=False)
        self.evaluator = EvaluationRunner(self.adapter)
        self.prompts = [{'prompt_id': prompt_id('problem'), 'prompt': 'problem'}]

    def test_resume_saved_answers_and_prepare_tasks(self):
        with tempfile.TemporaryDirectory() as directory:
            run_dir = Path(directory) / 'pilot'
            summary = generate_batch(iter(self.prompts), self.evaluator, run_dir)
            self.assertEqual(summary['generated'], 1)
            summary = generate_batch(iter(self.prompts), self.evaluator, run_dir)
            self.assertEqual(summary['skipped'], 1)
            self.client.generate.assert_called_once()
            self.assertEqual(self.client.generate.call_args.kwargs['system'], CODING_SYSTEM)
            self.assertIs(self.client.generate.call_args.kwargs['think'], False)
            tasks = run_dir / 'sandbox_tasks.jsonl'
            summary = prepare_sandbox_tasks(run_dir / 'responses.jsonl', tasks)
            self.assertEqual(summary['pending_test_spec'], 1)
            task = list(read_jsonl(tasks))[0]
            self.assertEqual(task['code'], 'print(1)')
            self.assertIsNone(task['test_spec'])
            self.assertFalse(task['limits']['network_enabled'])
            self.assertEqual(task['prompt_id'], self.prompts[0]['prompt_id'])

    def test_retry_errors_and_preserve_attempt_history(self):
        with tempfile.TemporaryDirectory() as directory:
            self.client.generate.side_effect = RuntimeError('offline')
            summary = generate_batch(self.prompts, self.evaluator, directory)
            self.assertEqual(summary['generation_error'], 1)
            self.client.generate.side_effect = None
            generate_batch(self.prompts, self.evaluator, directory)
            records = list(read_jsonl(Path(directory) / 'responses.jsonl'))
            self.assertEqual([r['attempt'] for r in records], [1, 2])
            self.assertNotEqual(records[0]['response_id'], records[1]['response_id'])

    def test_reject_changed_run_configuration_before_inference(self):
        with tempfile.TemporaryDirectory() as directory:
            generate_batch(self.prompts, self.evaluator, directory)
            self.adapter.options['seed'] = 1
            with self.assertRaisesRegex(ValueError, 'configuration changed'):
                generate_batch(self.prompts, self.evaluator, directory)
            self.client.generate.assert_called_once()

    def test_truncated_generation_is_not_a_runnable_task(self):
        with tempfile.TemporaryDirectory() as directory:
            self.client.generate.return_value.model_dump.return_value['done_reason'] = 'length'
            generate_batch(self.prompts, self.evaluator, directory)
            summary = prepare_sandbox_tasks(Path(directory) / 'responses.jsonl', Path(directory) / 'tasks.jsonl')
            self.assertEqual(summary['incomplete_generation'], 1)

    def test_loading_validates_lazily_with_stable_ids(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / 'prompts.jsonl'
            path.write_text(json.dumps({'prompt': '  problema  '}) + '\nINVALID\n')
            prompt = list(load_prompts(path, limit=1))[0]
            self.assertEqual(prompt['prompt_id'], prompt_id('problema'))
            self.assertEqual(prompt['prompt'], '  problema  ')
            with self.assertRaisesRegex(ValueError, 'Invalid JSON'):
                list(load_prompts(path))
            with self.assertRaises(ValueError):
                list(load_prompts(path, limit=0))

    def test_ambiguous_code_is_rejected_without_execution(self):
        self.assertIsNone(extract_python('print(1)'))
        self.assertIsNone(extract_python('```python\nprint(1)\n```\n```python\nprint(2)\n```'))
        self.assertIsNone(extract_python('```bash\necho test\n```'))
        self.assertEqual(extract_python('```python\nraise RuntimeError()\n```'), 'raise RuntimeError()')
        with self.assertRaises(ValueError):
            SandboxLimits(wall_time_seconds=0)
        with self.assertRaises(ValueError):
            SandboxLimits(network_enabled=True)

    def test_interactive_problem_needs_a_dedicated_judge(self):
        with tempfile.TemporaryDirectory() as directory:
            text = "This is an interactive problem. Solve it."
            prompts = [{"prompt_id": prompt_id(text), "prompt": text}]
            generate_batch(prompts, self.evaluator, directory)
            summary = prepare_sandbox_tasks(Path(directory) / 'responses.jsonl', Path(directory) / 'tasks.jsonl')
            self.assertEqual(summary['requires_interactive_judge'], 1)
