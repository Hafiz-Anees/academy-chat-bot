"""Send messages via Instagram Messaging API."""
import os
import requests
from dotenv import load_dotenv
load_dotenv()

INSTAGRAM_TOKEN = os.getenv("INSTAGRAM_TOKEN")
INSTAGRAM_ACCOUNT_ID = os.getenv("INSTAGRAM_ACCOUNT_ID")  # the Instagram Business Account ID (not the @handle)

GRAPH_URL = f"https://graph.instagram.com/v25.0/{INSTAGRAM_ACCOUNT_ID}/messages"

"""For chat messages"""

def send_instagram_message(recipient_id: str, body: str):
    headers = {
        "Authorization": f"Bearer {INSTAGRAM_TOKEN}",
        "Content-Type": "application/json",
    }
    payload = {
        "recipient": {"id": recipient_id},
        "message": {"text": body},
    }
    r = requests.post(GRAPH_URL, headers=headers, json=payload, timeout=15)
    print(f"Instagram send response [{r.status_code}]: {r.text}")  # TEMP debug line
    r.raise_for_status()
    return r.json()