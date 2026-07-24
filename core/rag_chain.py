"""Retrieval + prompt + LLM response, with scope guardrails and registration tool-calling."""
from langchain_core.messages import SystemMessage, HumanMessage, AIMessage, ToolMessage
from core.vectorstore import search
from core.llm import get_llm
from core.database import (
    register_student as db_register_student,
    check_registration as db_check_registration,
)
from tools.registration import REGISTRATION_TOOLS
from scripts.llm_prompt import get_prompt

SYSTEM_PROMPT = get_prompt()


def build_context(chunks: list[dict]) -> str:
    if not chunks:
        return "No relevant information found."
    return "\n\n".join(f"[{c.get('category', 'general')}] {c['text']}" for c in chunks)


def get_response(
    query: str,
    chat_history: list[dict] = None,
    academy_name: str = "Anees education system",
    phone_number: str = None,
) -> str:
    """
    chat_history: [{'role': 'user'|'assistant', 'content': str}, ...]
    phone_number: known phone number of the user (WhatsApp). None for website chat.
    """
    chat_history = chat_history or []
    chunks = search(query)
    context = build_context(chunks)

    system_text = SYSTEM_PROMPT.format(academy_name=academy_name)
    if phone_number:
        system_text += (
            f"\n\nThe user's phone number is already known: {phone_number}. "
            f"Do NOT ask the user for their phone number, use this value directly "
            f"if you need to call the register_student or check_registration tool."
        )

    messages = [SystemMessage(content=system_text)]
    for turn in chat_history[-30:]:
        if turn["role"] == "user":
            messages.append(HumanMessage(content=turn["content"]))
        else:
            messages.append(AIMessage(content=turn["content"]))

    messages.append(
        HumanMessage(
            content=(
                f"{query}\n\n"
                f"(Reference academy information, if relevant to this message: {context})"
            )
        )
    )

    llm = get_llm()
    llm_with_tools = llm.bind_tools(REGISTRATION_TOOLS)

    response = llm_with_tools.invoke(messages)

    # No tool call -> normal RAG reply
    if not getattr(response, "tool_calls", None):
        return response.content

    # Tool call path
    messages.append(response)

    for tool_call in response.tool_calls:
        if tool_call["name"] == "register_student":
            args = tool_call["args"]

            # Never trust the LLM's own phone_number if we already know it
            final_phone = phone_number or args.get("phone_number")

            result = db_register_student(
                phone_number=final_phone,
                name=args.get("name"),
                student_class=args.get("student_class"),
                email=args.get("email"),
            )

            messages.append(
                ToolMessage(
                    content=str(result),
                    tool_call_id=tool_call["id"],
                )
            )

        elif tool_call["name"] == "check_registration":
            args = tool_call["args"]

            # SECURITY: on WhatsApp, ALWAYS use the real phone_number from the
            # webhook. Never let the LLM substitute a different number, so a
            # user can never look up someone else's registration.
            if phone_number:
                result = db_check_registration(phone_number=phone_number)
            else:
                result = db_check_registration(email=args.get("email"))

            messages.append(
                ToolMessage(
                    content=str(result),
                    tool_call_id=tool_call["id"],
                )
            )

        else:
            messages.append(
                ToolMessage(
                    content="Unknown tool.",
                    tool_call_id=tool_call["id"],
                )
            )

    # Call the LLM again so it can turn the tool result into a natural reply
    final_response = llm_with_tools.invoke(messages)
    return final_response.content