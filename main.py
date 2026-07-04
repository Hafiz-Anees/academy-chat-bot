from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from core.rag_chain import get_response

app = FastAPI(title="Academy Admissions Agent API")

# Allow your Streamlit frontend (any origin for now — restrict later to frontend's Render URL)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Simple in-memory session store: {session_id: [{"role":..., "content":...}]}
sessions: dict[str, list] = {}


class ChatRequest(BaseModel):
    session_id: str
    message: str


class ChatResponse(BaseModel):
    reply: str


@app.get("/health")
def health():
    return {"status": "ok"}


@app.post("/chat", response_model=ChatResponse)
def chat(req: ChatRequest):
    history = sessions.setdefault(req.session_id, [])
    reply = get_response(req.message, chat_history=history)
    history.append({"role": "user", "content": req.message})
    history.append({"role": "assistant", "content": reply})
    return ChatResponse(reply=reply)


@app.get("/debug-env")
def debug_env():
    from config import QDRANT_URL
    return {"qdrant_url_repr": repr(QDRANT_URL)}