"""Groq LLM wrapper via LangChain."""
import os
from dotenv import load_dotenv
from langchain_groq import ChatGroq

load_dotenv()

GROQ_API_KEY = os.getenv("GROQ_API_KEY")
GROQ_MODEL = os.getenv("GROQ_MODEL")

_llm = None


def get_llm(temperature: float = 0.3) -> ChatGroq:
    global _llm
    if _llm is None:
        _llm = ChatGroq(api_key=GROQ_API_KEY, model=GROQ_MODEL, temperature=temperature)
    return _llm