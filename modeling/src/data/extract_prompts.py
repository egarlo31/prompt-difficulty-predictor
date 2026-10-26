"""Extract only prompt text from local TACO Arrow shards; no LLM required."""
import argparse
from collections import Counter
import hashlib
import json
from pathlib import Path
import tempfile

MODELING = Path(__file__).resolve().parents[2]


def iter_questions(raw_dir, splits):
    """Read record batches without loading solutions or tests into Python objects."""
    import pyarrow as pa

    for split in splits:
        files = sorted((raw_dir / split).glob('*.arrow'))
        if not files:
            raise FileNotFoundError(f'No Arrow shards in {raw_dir / split}')
        for path in files:
            with pa.memory_map(str(path), 'r') as source:
                reader = pa.ipc.open_stream(source)
                if 'question' not in reader.schema.names:
                    raise ValueError(f'Missing question column: {path}')
                for batch in reader:
                    yield from batch.column(batch.schema.get_field_index('question')).to_pylist()


def export_prompts(questions, destination, *, min_chars=1, deduplicate=True):
    """Write UTF-8 JSONL with exactly one `prompt` field per row, atomically.

    Whitespace is used only for validation and duplicate detection. The exported
    text preserves the original statement, including examples and whitespace.
    """
    if min_chars < 1:
        raise ValueError('min_chars must be positive')
    destination = Path(destination)
    destination.parent.mkdir(parents=True, exist_ok=True)
    counts = Counter(read=0, exported=0, empty_or_short=0, duplicates=0)
    seen = set()
    temporary = None
    try:
        with tempfile.NamedTemporaryFile(mode='w', encoding='utf-8', dir=destination.parent,
                                         suffix='.tmp', delete=False) as output:
            temporary = Path(output.name)
            for question in questions:
                counts['read'] += 1
                if question is not None and not isinstance(question, str):
                    raise ValueError('Expected question to be text or null')
                normalized = (question or '').strip()
                if len(normalized) < min_chars:
                    counts['empty_or_short'] += 1
                    continue
                digest = hashlib.sha256(normalized.encode('utf-8')).digest()
                if deduplicate and digest in seen:
                    counts['duplicates'] += 1
                    continue
                if deduplicate:
                    seen.add(digest)
                output.write(json.dumps({'prompt': question}, ensure_ascii=False) + '\n')
                counts['exported'] += 1
        temporary.replace(destination)
    finally:
        if temporary is not None:
            temporary.unlink(missing_ok=True)
    return dict(counts)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--raw-dir', type=Path, default=MODELING / 'data/raw/TACO')
    parser.add_argument('--output', type=Path, default=MODELING / 'data/processed/prompts.jsonl')
    parser.add_argument('--split', choices=['train', 'test', 'all'], default='all')
    parser.add_argument('--min-chars', type=int, default=1)
    parser.add_argument('--keep-duplicates', action='store_true')
    args = parser.parse_args()
    if args.min_chars < 1:
        parser.error('--min-chars must be positive')
    splits = ['train', 'test'] if args.split == 'all' else [args.split]
    raw = args.raw_dir.resolve()
    output = args.output.resolve()
    if output == raw or raw in output.parents:
        parser.error('--output must be outside the raw data directory')
    counts = export_prompts(iter_questions(raw, splits), output,
                            min_chars=args.min_chars, deduplicate=not args.keep_duplicates)
    print(json.dumps(counts, ensure_ascii=False, indent=2))
    print(f'Prompts: {output}')


if __name__ == '__main__':
    main()
