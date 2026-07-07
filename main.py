import asyncio
from fastapi import FastAPI, Request, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from core.rag_chain import get_response
from core.whatsapp import send_whatsapp_message
import os

app = FastAPI(title="Academy Admissions Agent API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Simple in-memory session store: {session_id: [{"role":..., "content":...}]}
sessions: dict[str, list] = {}

# Guard against Meta re-delivering the same webhook event
processed_message_ids: set[str] = set()

# One lock per user so their messages are handled in order, never concurrently
user_locks: dict[str, asyncio.Lock] = {}


def get_user_lock(user_id: str) -> asyncio.Lock:
    if user_id not in user_locks:
        user_locks[user_id] = asyncio.Lock()
    return user_locks[user_id]


@app.on_event("startup")
async def startup_event():
    from core.embeddings import get_embedder
    from core.vectorstore import get_client, ensure_collection

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


async def process_message(from_number: str, text: str):
    """Runs after the webhook has already ack'd Meta — safe to take as long as needed."""
    lock = get_user_lock(from_number)
    async with lock:
        history = sessions.setdefault(from_number, [])
        reply = get_response(text, chat_history=history)
        history.append({"role": "user", "content": text})
        history.append({"role": "assistant", "content": reply})
        send_whatsapp_message(from_number, reply)
        print(f"Sent WhatsApp message to {from_number}: {reply}")


# --- Incoming messages ---
@app.post("/webhook")
async def receive_whatsapp(request: Request, background_tasks: BackgroundTasks):
    data = await request.json()
    try:
        entry = data["entry"][0]
        changes = entry["changes"][0]
        value = changes["value"]

        if "messages" not in value:
            # Could be a status update (delivered/read) — ignore
            return {"status": "ignored"}

        message = value["messages"][0]
        from_number = message["from"]
        text = message["text"]["body"]
        msg_id = message["id"]  # WhatsApp's unique message ID

        print(f"Received message from {from_number}: {text}")

        # Guard against Meta re-delivering the same webhook event
        if msg_id in processed_message_ids:
            print(f"Duplicate message {msg_id} ignored.")
            return {"status": "duplicate_ignored"}
        processed_message_ids.add(msg_id)

        # Ack Meta immediately — do the slow RAG/LLM work in the background
        background_tasks.add_task(process_message, from_number, text)

    except (KeyError, IndexError) as e:
        print(f"Webhook parse error (likely a non-message event): {e}")

    return {"status": "received"}



# from fastapi import FastAPI
# from fastapi.middleware.cors import CORSMiddleware
# from pydantic import BaseModel
# from core.rag_chain import get_response
# from fastapi import Request
# import os
# from core.whatsapp import send_whatsapp_message
# import json
# app = FastAPI(title="Academy Admissions Agent API")

# # Allow your Streamlit frontend (any origin for now — restrict later to frontend's Render URL)
# app.add_middleware(
#     CORSMiddleware,
#     allow_origins=["*"],
#     allow_methods=["*"],
#     allow_headers=["*"],
# )

# # Simple in-memory session store: {session_id: [{"role":..., "content":...}]}
# sessions: dict[str, list] = {}


# class ChatRequest(BaseModel):
#     session_id: str
#     message: str


# class ChatResponse(BaseModel):
#     reply: str


# @app.get("/health")
# def health():
#     return {"status": "ok"}


# @app.post("/chat", response_model=ChatResponse)
# def chat(req: ChatRequest):
#     history = sessions.setdefault(req.session_id, [])
#     reply = get_response(req.message, chat_history=history)
#     history.append({"role": "user", "content": req.message})
#     history.append({"role": "assistant", "content": reply})
#     return ChatResponse(reply=reply)




# WHATSAPP_VERIFY_TOKEN = os.getenv("WHATSAPP_VERIFY_TOKEN")

# # --- Webhook verification (Meta calls this once when you set up the webhook) ---
# @app.get("/webhook")
# def verify_webhook(request: Request):
#     params = request.query_params
#     mode = params.get("hub.mode")
#     token = params.get("hub.verify_token")
#     challenge = params.get("hub.challenge")

#     if mode == "subscribe" and token == WHATSAPP_VERIFY_TOKEN:
#         return int(challenge)
#     return {"error": "verification failed"}, 403


# # --- Incoming messages ---
# @app.post("/webhook")
# async def receive_whatsapp(request: Request):
#     data = await request.json()
#     try:
#         entry = data["entry"][0]
#         changes = entry["changes"][0]
#         value = changes["value"]

#         if "messages" not in value:
#             # Could be a status update (delivered/read) — ignore
#             return {"status": "ignored"}

#         message = value["messages"][0]
#         from_number = message["from"]  # sender's WhatsApp number
#         text = message["text"]["body"]

#         print(f"Received message from {from_number}: {text}")
#         # Use phone number as session_id so each user gets their own conversation memory
#         history = sessions.setdefault(from_number, [])
#         reply = get_response(text, chat_history=history)
#         history.append({"role": "user", "content": text})
#         history.append({"role": "assistant", "content": reply})

#         send_whatsapp_message(from_number, reply)

#     except (KeyError, IndexError) as e:
#         print(f"Webhook parse error (likely a non-message event): {e}")

#     return {"status": "received"}