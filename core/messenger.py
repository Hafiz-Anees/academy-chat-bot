"""Send messages via Messenger (Facebook Page) API."""
import os
import requests
from dotenv import load_dotenv
load_dotenv()

MESSENGER_PAGE_ACCESS_TOKEN = os.getenv("MESSENGER_PAGE_ACCESS_TOKEN")

GRAPH_URL = "https://graph.facebook.com/v25.0/me/messages"

"""For chat messages"""

def send_messenger_message(recipient_id: str, body: str):
    params = {
        "access_token": MESSENGER_PAGE_ACCESS_TOKEN,
    }
    headers = {
        "Content-Type": "application/json",
    }
    payload = {
        "recipient": {"id": recipient_id},
        "message": {"text": body},
        "messaging_type": "RESPONSE",
    }
    r = requests.post(GRAPH_URL, headers=headers, params=params, json=payload, timeout=15)
    print(f"Messenger send response [{r.status_code}]: {r.text}")  # TEMP debug line
    r.raise_for_status()
    return r.json()