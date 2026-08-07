import os
import shutil
import tempfile
from langchain_google_community._utils import get_google_credentials
from langchain_google_community.gmail.utils import build_resource_service
from langchain_google_community.gmail.send_message import GmailSendMessage
import logging

logger = logging.getLogger(__name__)

CREDENTIALS_PATH = os.getenv("GMAIL_CREDENTIALS_PATH", "credentials.json")
TOKEN_SOURCE_PATH = os.getenv("GMAIL_TOKEN_PATH", "token.json")

# The token file must be writable (the library rewrites it after loading/refreshing).
# Secret-mounted paths (Render /etc/secrets, Cloud Run secret volumes) are read-only,
# so copy it to a writable temp location first.
TOKEN_PATH = os.path.join(tempfile.gettempdir(), "gmail_token.json")
shutil.copyfile(TOKEN_SOURCE_PATH, TOKEN_PATH)

_credentials = get_google_credentials(
    token_file=TOKEN_PATH,
    client_secrets_file=CREDENTIALS_PATH,
    scopes=["https://www.googleapis.com/auth/gmail.send"],
)
_api_resource = build_resource_service(credentials=_credentials)
_gmail_tool = GmailSendMessage(api_resource=_api_resource)

ADMIN_EMAIL = "hafizrehmananees786@gmail.com"


def send_registration_emails(name: str, email: str, phone: str, grade: str):
    print(f"[EMAIL DEBUG] send_registration_emails called with: {name}, {email}, {phone}, {grade}")
    try:
        _gmail_tool.run({
            "to": email,
            "subject": "Registration Confirmed - Anees Education System",
            "message": (
                f"Hi {name},\n\n"
                f"Your registration for Grade {grade} has been received successfully.\n"
                f"We'll be in touch with next steps shortly.\n\n"
                f"Regards,\nAnees Education System"
            ),
        })
        print(f"[EMAIL DEBUG] Student email sent successfully to {email}")
    except Exception as e:
        print(f"[EMAIL DEBUG] STUDENT EMAIL FAILED: {e}")

    try:
        _gmail_tool.run({
            "to": ADMIN_EMAIL,
            "subject": f"New Registration: {name}",
            "message": (
                f"A new student has registered.\n\n"
                f"Name: {name}\n"
                f"Email: {email}\n"
                f"Phone: {phone}\n"
                f"Grade: {grade}"
            ),
        })
        print(f"[EMAIL DEBUG] Admin email sent successfully")
    except Exception as e:
        print(f"[EMAIL DEBUG] ADMIN EMAIL FAILED: {e}")