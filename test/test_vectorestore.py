import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent))

from core.vectorstore import reset_collection, upsert_chunks, search
from ingestion.chunker import load_and_chunk

def run():
    print("Resetting Qdrant collection (clean slate)...")
    reset_collection()

    chunks = load_and_chunk()
    print(f"Loaded {len(chunks)} chunks from your .md files")
    assert len(chunks) > 0, "No chunks found"

    print("Upserting chunks into Qdrant...")
    upsert_chunks(chunks)

    query = input("\nEnter a test question about your academy: ").strip()
    if not query:
        query = "What courses do you offer?"

    print(f"\nSearching: '{query}'")
    results = search(query, top_k=3)

    for r in results:
        print(f"  score={r['score']:.3f} [{r['category']}] {r['text'][:100]}...")

    assert len(results) > 0, "No search results returned"
    print("\n✓ Search returned relevant results")
    print("Component 2 (Vectorstore) PASSED")

if __name__ == "__main__":
    run()