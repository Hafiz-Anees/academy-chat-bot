"""
Component 1 test: Embeddings
Run: python test/test_embeddings.py

Checks:
- Model loads without error
- Output vector has expected dimension (384 for bge-small-en-v1.5)
- Similar sentences get higher cosine similarity than dissimilar ones
"""
import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent))

import numpy as np
from core.embeddings import embed_texts
from config import EMBEDDING_DIM


def cosine_sim(a, b):
    a, b = np.array(a), np.array(b)
    return np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b))


def run():
    texts = [
        "What is the fee for the Web Development course?",
        "How much does the Web Development course cost?",
        "What is the weather today?",
    ]
    print("Embedding sample texts...")
    vectors = embed_texts(texts)

    assert len(vectors) == 3, "Expected 3 vectors"
    assert len(vectors[0]) == EMBEDDING_DIM, f"Expected dim {EMBEDDING_DIM}, got {len(vectors[0])}"
    print(f"✓ Vector dimension correct: {len(vectors[0])}")

    sim_related = cosine_sim(vectors[0], vectors[1])
    sim_unrelated = cosine_sim(vectors[0], vectors[2])
    print(f"Similarity (fee questions, related): {sim_related:.3f}")
    print(f"Similarity (fee vs weather, unrelated): {sim_unrelated:.3f}")

    assert sim_related > sim_unrelated, "Related sentences should be more similar than unrelated ones"
    print("✓ Semantic similarity behaves as expected")
    print("\nComponent 1 (Embeddings) PASSED")


if __name__ == "__main__":
    run()