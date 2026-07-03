"""
Component 3 test: Groq LLM
Run: python test/test_llm.py

Checks:
- Groq API key works
- Model responds to a basic prompt
"""
import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent))

from langchain_core.messages import HumanMessage
from core.llm import get_llm

def run():
    llm = get_llm()
    print("Sending test prompt to Groq...")
    response = llm.invoke([HumanMessage(content="Reply with exactly: 'Groq is working'")])
    print(f"Response: {response.content}")

    assert response.content, "Empty response from LLM"
    print("\nComponent 3 (LLM) PASSED")

if __name__ == "__main__":
    run()