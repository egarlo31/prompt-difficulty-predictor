import unittest
from types import SimpleNamespace
from unittest.mock import Mock
from backend.local_llm.ollama_adapter import OllamaAdapter


class OllamaAdapterTests(unittest.TestCase):
    def setUp(self):
        self.client = Mock()
        self.client.generate.return_value = SimpleNamespace(response="answer")
        self.options = {"temperature": 0, "num_predict": 512}
        self.adapter = OllamaAdapter("test", client=self.client, options=self.options)

    def test_text_and_full_response(self):
        self.assertEqual(self.adapter.generate("question"), "answer")
        self.assertIs(self.adapter.generate_result("question"), self.client.generate.return_value)
        self.client.generate.assert_called_with(model="test", prompt="question", stream=False,
            options=self.options, keep_alive="10m")

    def test_warmup_and_overrides_do_not_mutate_defaults(self):
        self.adapter.warm_up()
        self.assertEqual(self.client.generate.call_args.kwargs["options"]["num_predict"], 1)
        self.adapter.generate("question", options={"temperature": 0.5})
        self.assertEqual(self.client.generate.call_args.kwargs["options"]["temperature"], 0.5)
        self.assertEqual(self.adapter.options, self.options)

    def test_failure_propagates(self):
        self.client.generate.side_effect = RuntimeError("offline")
        with self.assertRaisesRegex(RuntimeError, "offline"):
            self.adapter.generate("question")


class EvaluationIntegrationTests(unittest.TestCase):
    def test_evaluator_preserves_response_metrics_through_adapter(self):
        from unittest.mock import patch
        from modeling.src.evaluation.generate_responses import LLMGeneration
        client = Mock()
        client.generate.return_value.model_dump.return_value = {
            "response": "answer", "total_duration": 3_000_000_000,
            "load_duration": 1_000_000_000,
        }
        with patch("modeling.src.evaluation.generate_responses.HardwareMonitor") as monitor:
            monitor.return_value.calculate_resource_metrics.return_value = {}
            generator = LLMGeneration(client, None, "test", {"seed": 42})
            record = generator.generate_response("question")
        self.assertEqual(record["status"], "generated")
        self.assertEqual(record["response"], "answer")
        self.assertEqual(record["processing_duration_seconds"], 2.0)
        client.generate.assert_called_once_with(model="test", prompt="question", stream=False,
                                               options={"seed": 42}, keep_alive="10m")
