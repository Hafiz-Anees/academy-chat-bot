import os
from fastapi import APIRouter, BackgroundTasks, Request
from scripts.state import processed_message_ids
from scripts.handlers import process_message, process_voice_message, process_instagram_message

router = APIRouter(tags=["WhatsApp Webhook"])

WHATSAPP_VERIFY_TOKEN = os.getenv("WHATSAPP_VERIFY_TOKEN")


@router.get("/webhook")
def verify_webhook(request: Request):
    params = request.query_params
    mode = params.get("hub.mode")
    token = params.get("hub.verify_token")
    challenge = params.get("hub.challenge")

    if mode == "subscribe" and token == WHATSAPP_VERIFY_TOKEN:
        return int(challenge)
    return {"error": "verification failed"}, 403


@router.post("/webhook")
async def receive_whatsapp(request: Request, background_tasks: BackgroundTasks):
    data = await request.json()

    # NEW: route Instagram payloads separately, leave WhatsApp logic untouched below
    if data.get("object") == "instagram":
        return await receive_instagram(data, background_tasks)

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

        if message.get("type") == "audio":
            media_id = message["audio"]["id"]
            print(f"Received voice message from {from_number}, media_id={media_id}")
            background_tasks.add_task(process_voice_message, from_number, media_id)
            return {"status": "received"}

        text = message["text"]["body"]
        print(f"Received message from {from_number}: {text}")
        background_tasks.add_task(process_message, from_number, text)

    except (KeyError, IndexError) as e:
        print(f"Webhook parse error (likely a non-message event): {e}")

    return {"status": "received"}


# NEW: Instagram-specific handler, kept separate from WhatsApp logic
async def receive_instagram(data: dict, background_tasks: BackgroundTasks):
    try:
        entry = data["entry"][0]
        messaging_event = entry["messaging"][0]

        # Skip echo messages (Meta re-delivers messages your bot itself sent)
        if messaging_event.get("message", {}).get("is_echo"):
            return {"status": "ignored_echo"}

        sender_id = messaging_event["sender"]["id"]
        message = messaging_event.get("message", {})
        msg_id = message.get("mid")

        if not msg_id:
            return {"status": "ignored"}

        if msg_id in processed_message_ids:
            print(f"Duplicate Instagram message {msg_id} ignored.")
            return {"status": "duplicate_ignored"}
        processed_message_ids.add(msg_id)

        text = message.get("text")
        if not text:
            print(f"Non-text Instagram message from {sender_id}, skipping for now.")
            return {"status": "ignored_non_text"}

        print(f"Received Instagram message from {sender_id}: {text}")
        background_tasks.add_task(process_instagram_message, sender_id, text)

    except (KeyError, IndexError) as e:
        print(f"Instagram webhook parse error (likely a non-message event): {e}")

    return {"status": "received"}