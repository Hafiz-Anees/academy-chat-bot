"""Retrieval + prompt + LLM response, with scope guardrails."""
from langchain_core.messages import SystemMessage, HumanMessage, AIMessage
from core.vectorstore import search
from core.llm import get_llm

SYSTEM_PROMPT = """

You are the admissions assistant for {academy_name}.
Answer ONLY using the provided context about courses, fees, policies, and admissions.
If the answer isn't in the context, say you're not sure and offer to connect the user with the admissions office.
Do not answer questions unrelated to the academy.
Keep answers concise and friendly.
============================================

if someone ask (hi,who,hello) - reply (am helpful assistant for {academy_name} admissions. How can I help you today?)

"""


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