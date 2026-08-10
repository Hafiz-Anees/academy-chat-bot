"""Ingest all markdown docs from data/academy_docs/ into Qdrant with
both dense and sparse vectors. Run this whenever docs change.
"""
import sys
from pathlib import Path

sys.path.append(str(Path(__file__).parent.parent))

from ingestion.chunker import load_and_chunk
from core.vectorstore import reset_collection, upsert_chunks


def main():
    print("1) Loading and chunking markdown files...")
    chunks = load_and_chunk()
    print(f"   loaded {len(chunks)} chunks from data/academy_docs/\n")

    if not chunks:
        print("   NO CHUNKS FOUND — check DATA_DIR path in chunks.py. Aborting.")
        return

    print("2) Resetting Qdrant collection (dense + sparse schema)...")
    reset_collection()
    print("   done.\n")

    print("3) Embedding + upserting chunks (dense + sparse)...")
    # batch upserts if you have a large corpus, to avoid one giant request
    batch_size = 64
    for i in range(0, len(chunks), batch_size):
        batch = chunks[i : i + batch_size]
        upsert_chunks(batch)
        print(f"   upserted {i + len(batch)}/{len(chunks)}")

    print("\nDone. Collection now has both dense and sparse vectors for all chunks.")


if __name__ == "__main__":
    main()