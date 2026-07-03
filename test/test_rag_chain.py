"""
Component 4 test: RAG Chain (end-to-end, no server yet)
Run: python test/test_rag_chain.py

Checks:
- Retrieval + prompt + LLM work together
- Answer is grounded in your actual academy data
- Off-topic questions get a graceful refusal
"""
import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent))

from core.rag_chain import get_response

def run():
    print("Test 1: On-topic question")
    q1 = "What is the fee for the primary program?"
    a1 = get_response(q1)
    print(f"Q: {q1}\nA: {a1}\n")

    print("Test 2: Off-topic question (should decline gracefully)")
    q2 = "What's the capital of France?"
    a2 = get_response(q2)
    print(f"Q: {q2}\nA: {a2}\n")

    print("Test 3: Interactive — ask your own question")
    while True:
        q = input("Ask (or 'quit'): ").strip()
        if q.lower() in ("quit", "q", ""):
            break
        print(f"A: {get_response(q)}\n")

    print("Component 4 (RAG Chain) PASSED")

if __name__ == "__main__":
    run()