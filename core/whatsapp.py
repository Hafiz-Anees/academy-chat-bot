"""Send messages via WhatsApp Cloud API."""
import os
import requests

WHATSAPP_TOKEN = os.getenv("WHATSAPP_TOKEN")
WHATSAPP_PHONE_NUMBER_ID = os.getenv("WHATSAPP_PHONE_NUMBER_ID")

GRAPH_URL = f"https://graph.facebook.com/v21.0/{WHATSAPP_PHONE_NUMBER_ID}/messages"


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