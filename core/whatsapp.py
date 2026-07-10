"""Send messages via WhatsApp Cloud API."""
import os
import requests
from dotenv import load_dotenv
load_dotenv() 
WHATSAPP_TOKEN = os.getenv("WHATSAPP_TOKEN")
WHATSAPP_PHONE_NUMBER_ID = os.getenv("WHATSAPP_PHONE_NUMBER_ID")

GRAPH_URL = f"https://graph.facebook.com/v25.0/{WHATSAPP_PHONE_NUMBER_ID}/messages"


def send_whatsapp_message(to: str, body: str):
    """to: recipient phone number in international format, no '+' (e.g. '923001234567')"""
    headers = {
        "Authorization": f"Bearer {WHATSAPP_TOKEN}",
        "Content-Type": "application/json",
    }
    payload = {
        "messaging_product": "whatsapp",
        "to": to,
        "type": "text",
        "text": {"body": body},
    }
    r = requests.post(GRAPH_URL, headers=headers, json=payload, timeout=15)
    r.raise_for_status()
    return r.json()


# for voice message

def get_media_url(media_id: str) -> str:
    """Step 1a: resolve a media_id (from an incoming voice message) into a
    temporary, authenticated download URL."""
    url = f"https://graph.facebook.com/v25.0/{media_id}"
    headers = {"Authorization": f"Bearer {WHATSAPP_TOKEN}"}
    r = requests.get(url, headers=headers, timeout=15)
    r.raise_for_status()
    return r.json()["url"]


def download_media(media_id: str) -> bytes:
    """Step 1b: download the actual audio bytes using the resolved URL."""
    media_url = get_media_url(media_id)
    headers = {"Authorization": f"Bearer {WHATSAPP_TOKEN}"}
    r = requests.get(media_url, headers=headers, timeout=30)
    r.raise_for_status()
    return r.content