"""
Component 5 test: FastAPI Backend
Run:
  1. In one terminal: uvicorn main:app --reload
  2. In another terminal: python test/test_api.py
"""
import requests

BASE_URL = "http://127.0.0.1:8000"

def run():
    print("Testing /health...")
    r = requests.get(f"{BASE_URL}/health")
    assert r.status_code == 200
    print(f"✓ {r.json()}")

    print("\nTesting /chat...")
    r = requests.post(f"{BASE_URL}/chat", json={
        "session_id": "test-session-1",
        "message": "What is the fee for the primary program?"
    })
    assert r.status_code == 200
    print(f"✓ Reply: {r.json()['reply']}")

    print("\nTesting conversation memory (follow-up question)...")
    r = requests.post(f"{BASE_URL}/chat", json={
        "session_id": "test-session-1",
        "message": "What about secondary?"
    })
    print(f"✓ Reply: {r.json()['reply']}")

    print("\nComponent 5 (FastAPI Backend) PASSED")

if __name__ == "__main__":
    run()