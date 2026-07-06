from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from core.rag_chain import get_response
from fastapi import Request
import os
from core.whatsapp import send_whatsapp_message
import json
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




WHATSAPP_VERIFY_TOKEN = os.getenv("WHATSAPP_VERIFY_TOKEN")

# --- Webhook verification (Meta calls this once when you set up the webhook) ---
@app.get("/webhook")
def verify_webhook(request: Request):
    params = request.query_params
    mode = params.get("hub.mode")
    token = params.get("hub.verify_token")
    challenge = params.get("hub.challenge")

    if mode == "subscribe" and token == WHATSAPP_VERIFY_TOKEN:
        return int(challenge)
    return {"error": "verification failed"}, 403


# --- Incoming messages ---
@app.post("/webhook")
async def receive_whatsapp(request: Request):
    data = await request.json()
    try:
        entry = data["entry"][0]
        changes = entry["changes"][0]
        value = changes["value"]

        if "messages" not in value:
            # Could be a status update (delivered/read) — ignore
            return {"status": "ignored"}

        message = value["messages"][0]
        from_number = message["from"]  # sender's WhatsApp number
        text = message["text"]["body"]

        # Use phone number as session_id so each user gets their own conversation memory
        history = sessions.setdefault(from_number, [])
        reply = get_response(text, chat_history=history)
        history.append({"role": "user", "content": text})
        history.append({"role": "assistant", "content": reply})

        send_whatsapp_message(from_number, reply)

    except (KeyError, IndexError) as e:
        print(f"Webhook parse error (likely a non-message event): {e}")

    return {"status": "received"}