import unittest
from unittest.mock import Mock

from backend.local_llm.ollama_adapter import OllamaAdapter
from modeling.src.evaluation.generate_responses import EvaluationRunner


class OllamaAdapterTests(unittest.TestCase):
    def setUp(self):
        self.client = Mock()
        self.client.generate.return_value.response = "answer"
        self.adapter = OllamaAdapter("test", client=self.client, options={"seed": 42})

    def test_single_generate_returns_text_and_metrics_together(self):
        response = self.adapter.generate("question")
        self.assertIs(response, self.client.generate.return_value)
        self.assertEqual(response.response, "answer")
        self.client.generate.assert_called_once_with(
            model="test", prompt="question", stream=False,
            options={"seed": 42}, keep_alive="10m",
        )

    def test_overrides_and_warmup_preserve_defaults(self):
        self.adapter.generate("Warm-up.", options={"num_predict": 1, "seed": 0})
        self.assertEqual(self.client.generate.call_args.kwargs["options"], {"seed": 0, "num_predict": 1})
        self.assertEqual(self.adapter.options, {"seed": 42})

    def test_inference_errors_propagate(self):
        self.client.generate.side_effect = RuntimeError("offline")
        with self.assertRaisesRegex(RuntimeError, "offline"):
            self.adapter.generate("question")


class EvaluationTests(unittest.TestCase):
    def setUp(self):
        self.client = Mock()
        self.client.generate.return_value.model_dump.return_value = {
            "response": "answer", "total_duration": 3_000_000_000,
            "load_duration": 1_000_000_000,
        }
        self.adapter = OllamaAdapter("test", client=self.client, options={"seed": 42})

    def test_shared_adapter_retains_metrics_without_gpu(self):
        runner = EvaluationRunner(self.adapter)
        self.adapter.options["seed"] = 10
        record = runner.evaluate("question")
        self.assertIs(runner.adapter, self.adapter)
        self.assertEqual(record["status"], "generated")
        self.assertEqual(record["response"], "answer")
        self.assertEqual(record["processing_duration_seconds"], 2.0)
        self.assertIsNone(record["eval_duration_seconds"])
        self.assertEqual(record["resources"], {})
        self.assertEqual(record["inference_config"], {"seed": 10})
        self.client.generate.assert_called_once_with(
            model="test", prompt="question", stream=False,
            options={"seed": 10}, keep_alive="10m",
        )

    def test_error_record_stops_monitor_and_keeps_samples(self):
        import threading
        monitor = Mock()
        stopped = threading.Event()
        def monitor_resources(stop, samples):
            stop.wait(2)
            if stop.is_set():
                stopped.set()
        monitor.monitor_resources.side_effect = monitor_resources
        monitor.get_hardware_metrics.return_value = {"ram_gib": 1}
        monitor.calculate_resource_metrics.return_value = {"sample_count": 2}
        self.client.generate.side_effect = RuntimeError("offline")
        record = EvaluationRunner(self.adapter, monitor).evaluate("question")
        self.assertEqual(record["status"], "generation_error")
        self.assertEqual(record["error"], "offline")
        self.assertEqual(record["resources"], {"sample_count": 2})
        self.assertEqual(monitor.get_hardware_metrics.call_count, 2)
        self.assertTrue(stopped.is_set())
