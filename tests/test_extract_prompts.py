"""Tests for prompt-only export, independent of datasets and model providers."""
import json
from pathlib import Path
import tempfile
import unittest

from modeling.src.data.extract_prompts import export_prompts, iter_questions


class PromptExportTests(unittest.TestCase):
    def test_only_prompts_preserving_unicode_and_multiline(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / 'prompts.jsonl'
            stats = export_prompts(['  ¿Qué?\nEjemplo 1  ', '¿Qué?\nEjemplo 1', None, '  '], path)
            self.assertEqual(stats, dict(read=4, exported=1, empty_or_short=2, duplicates=1))
            self.assertEqual(json.loads(path.read_text()), {'prompt': '  ¿Qué?\nEjemplo 1  '})

    def test_options_and_atomic_failure(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / 'prompts.jsonl'
            stats = export_prompts(['abc', 'abc', 'x'], path, min_chars=3, deduplicate=False)
            self.assertEqual(stats['exported'], 2)
            original = path.read_text()
            with self.assertRaises(ValueError):
                export_prompts(['valid', 4], path)
            self.assertEqual(path.read_text(), original)
            self.assertEqual(list(Path(directory).glob('*.tmp')), [])

    def test_arrow_shards_and_missing_split(self):
        import pyarrow as pa
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / 'train').mkdir()
            for number, text in enumerate(['first', 'second']):
                table = pa.table({'question': [text], 'solutions': ['excluded']})
                with pa.OSFile(str(root / 'train' / f'{number}.arrow'), 'wb') as stream:
                    with pa.ipc.new_stream(stream, table.schema) as writer:
                        writer.write_table(table)
            self.assertEqual(list(iter_questions(root, ['train'])), ['first', 'second'])
            with self.assertRaises(FileNotFoundError):
                list(iter_questions(root, ['test']))


if __name__ == '__main__':
    unittest.main()
