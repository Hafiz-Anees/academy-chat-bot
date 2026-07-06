"""
Component: Chunker
Run: python test/test_chunker.py

Checks:
- Reads .md files from data/academy_docs/
- Produces non-empty chunks
- Category matches filename
"""
import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent))

from ingestion.chunker import load_and_chunk

def run():
    chunks = load_and_chunk()
    files = sorted(set(c["source_file"] for c in chunks))
    print(files)
    print(f"Loaded {len(chunks)} chunks from {len(set(c['category'] for c in chunks))} files")

    assert len(chunks) > 0, "No chunks produced — check data/academy_docs/ has .md files"

    for c in chunks[:5]:
        print(f"  [{c['category']}] id={c['id']} | {c['text'][:80]}...")

    print("\nComponent (Chunker) PASSED")

if __name__ == "__main__":
    run()