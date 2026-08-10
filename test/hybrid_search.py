"""Quick smoke test for hybrid (dense + sparse) ingestion and search.
Run this BEFORE wiring hybrid search into the main ingestion pipeline.
"""
import sys
from pathlib import Path

# adjust if your project root isn't two levels up from this file
sys.path.append(str(Path(__file__).parent.parent))

from core.vectorstore import reset_collection, upsert_chunks, search

# A handful of fake chunks that mimic your real chunk shape
sample_chunks = [
    {
        "id": 1001,
        "text": "NES Admissions\nStudents must submit transcripts and a passport-size photo to complete registration.",
        "category": "admissions",
        "title": "NES Admissions",
        "source_id": "adm-01",
        "source_file": "admissions.md",
    },
    {
        "id": 1002,
        "text": "Fee Structure\nTuition fees for the Computer Science program are due at the start of each semester.",
        "category": "fees",
        "title": "Fee Structure",
        "source_id": "fee-01",
        "source_file": "fees.md",
    },
    {
        "id": 1003,
        "text": "Hostel Facilities\nOn-campus hostel accommodation is available for out-of-city students on a first-come basis.",
        "category": "facilities",
        "title": "Hostel Facilities",
        "source_id": "fac-01",
        "source_file": "facilities.md",
    },
]

def main():
    print("1) Resetting collection (dense + sparse schema)...")
    reset_collection()
    print("   done.\n")

    print("2) Upserting sample chunks...")
    upsert_chunks(sample_chunks)
    print(f"   upserted {len(sample_chunks)} chunks.\n")

    test_queries = [
        "how do I register transcripts",   # should hit admissions (dense + sparse overlap)
        "hostel",                          # sparse-friendly exact keyword match
        "tuition due date",                # dense-friendly paraphrase, no exact overlap
    ]

    for q in test_queries:
        print(f"3) Query: {q!r}")
        results = search(q, top_k=3)
        if not results:
            print("   NO RESULTS — something's wrong.")
        for r in results:
            print(f"   score={r['score']:.4f}  category={r['category']:<12}  text={r['text'][:60]!r}")
        print()

if __name__ == "__main__":
    main()