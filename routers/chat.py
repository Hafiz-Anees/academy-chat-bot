from fastapi import APIRouter

from core.rag_chain import get_response
from scripts.state import sessions
from schemas import ChatRequest, ChatResponse

router = APIRouter(tags=["Chat"])


@router.post("/chat", response_model=ChatResponse)
def chat(req: ChatRequest):
    history = sessions.setdefault(req.session_id, [])
    print(f"history : {history}")

    reply = get_response(req.message, chat_history=history)

    history.append({"role": "user", "content": req.message})
    history.append({"role": "assistant", "content": reply})

    print(f"Session {req.session_id} - User: {req.message} | Assistant: {reply}")
    return ChatResponse(reply=reply)