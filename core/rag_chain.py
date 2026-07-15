"""Retrieval + prompt + LLM response, with scope guardrails."""
from langchain_core.messages import SystemMessage, HumanMessage, AIMessage
from core.vectorstore import search
from core.llm import get_llm
from scripts.llm_prompt import get_prompt

SYSTEM_PROMPT = get_prompt()

def build_context(chunks: list[dict]) -> str:
    if not chunks:
        return "No relevant information found."
    return "\n\n".join(f"[{c.get('category', 'general')}] {c['text']}" for c in chunks)


def get_response(query: str, chat_history: list[dict] = None, academy_name: str = "naseer education system") -> str:
    """chat_history: [{'role': 'user'|'assistant', 'content': str}, ...]"""
    chat_history = chat_history or []
    chunks = search(query)
    context = build_context(chunks)

    messages = [SystemMessage(content=SYSTEM_PROMPT.format(academy_name=academy_name))]
    for turn in chat_history[-6:]:
        if turn["role"] == "user":
            messages.append(HumanMessage(content=turn["content"]))
        else:
            messages.append(AIMessage(content=turn["content"]))

    messages.append(HumanMessage(content=f"Context:\n{context}\n\nQuestion: {query}"))

    llm = get_llm()
    response = llm.invoke(messages)
    return response.content