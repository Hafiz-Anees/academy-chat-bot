from fastapi import FastAPI, Request, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import os

from core.rag_chain import get_response
from scripts.state import sessions, processed_message_ids
from scripts.handlers import process_message, process_voice_message
from core.embeddings import get_embedder
from core.vectorstore import get_client, ensure_collection

app = FastAPI(title="Academy Admissions Agent API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
async def startup_event():
    

    print("Warming up embedding model...")
    get_embedder()

    print("Connecting to Qdrant...")
    get_client()
    ensure_collection()

    print("Startup warm-up complete.")


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
    print(f"history : {history}")
    reply = get_response(req.message, chat_history=history)
    history.append({"role": "user", "content": req.message})
    history.append({"role": "assistant", "content": reply})
    print(f"Session {req.session_id} - User: {req.message} | Assistant: {reply}")
    return ChatResponse(reply=reply)


WHATSAPP_VERIFY_TOKEN = os.getenv("WHATSAPP_VERIFY_TOKEN")


@app.get("/webhook")
def verify_webhook(request: Request):
    params = request.query_params
    mode = params.get("hub.mode")
    token = params.get("hub.verify_token")
    challenge = params.get("hub.challenge")

    if mode == "subscribe" and token == WHATSAPP_VERIFY_TOKEN:
        return int(challenge)
    return {"error": "verification failed"}, 403


@app.post("/webhook")
async def receive_whatsapp(request: Request, background_tasks: BackgroundTasks):
    data = await request.json()
    try:
        entry = data["entry"][0]
        changes = entry["changes"][0]
        value = changes["value"]

        if "messages" not in value:
            return {"status": "ignored"}

        message = value["messages"][0]
        msg_id = message["id"]
        from_number = message["from"]

        if msg_id in processed_message_ids:
            print(f"Duplicate message {msg_id} ignored.")
            return {"status": "duplicate_ignored"}
        processed_message_ids.add(msg_id)

        # Handle voice messages first, since they don't have a "text" field
        if message.get("type") == "audio":
            media_id = message["audio"]["id"]
            print(f"Received voice message from {from_number}, media_id={media_id}")
            background_tasks.add_task(process_voice_message, from_number, media_id) # for voice messages
            return {"status": "received"}

        text = message["text"]["body"]
        print(f"Received message from {from_number}: {text}")
        background_tasks.add_task(process_message, from_number, text)  # for chat messages 

    except (KeyError, IndexError) as e:
        print(f"Webhook parse error (likely a non-message event): {e}")

    return {"status": "received"}



