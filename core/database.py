"""Supabase client and student registration logic."""
import os
import re
from supabase import create_client, Client

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

_client: Client | None = None

EMAIL_RE = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")
PHONE_RE = re.compile(r"^\+?\d{7,15}$")


def get_supabase_client() -> Client:
    global _client
    if _client is None:
        if not SUPABASE_URL or not SUPABASE_KEY:
            raise RuntimeError("SUPABASE_URL / SUPABASE_KEY env vars are not set.")
        _client = create_client(SUPABASE_URL, SUPABASE_KEY)
    return _client


def _validate_fields(phone_number: str, name: str, student_class: str, email: str) -> list[str]:
    """Returns a list of validation error messages, empty if all valid."""
    errors = []

    if not name or not name.strip() or len(name.strip()) < 2:
        errors.append("name is missing or too short")

    if not student_class or not student_class.strip():
        errors.append("class/grade is missing")

    if not email or not EMAIL_RE.match(email.strip()):
        errors.append("email is missing or not a valid email address")

    # Strip common formatting chars before checking phone digits
    cleaned_phone = re.sub(r"[\s\-()]", "", phone_number or "")
    if not cleaned_phone or not PHONE_RE.match(cleaned_phone):
        errors.append("phone number is missing or not a valid phone number")

    return errors


def check_registration(phone_number: str = None, email: str = None) -> dict:
    """
    Looks up a registration by phone_number (preferred, WhatsApp) or email
    (website chat fallback). Returns MINIMAL info only (no phone/email echoed
    back) to avoid leaking full records if this is ever misused for
    enumeration.
    """
    client = get_supabase_client()
    try:
        query = client.table("students").select("name, class")

        if phone_number:
            query = query.eq("phone_number", phone_number)
        elif email:
            query = query.eq("email", email)
        else:
            return {"found": False, "message": "No identifier provided."}

        result = query.execute()

        if result.data:
            record = result.data[0]
            return {
                "found": True,
                "name": record["name"],
                "class": record["class"],
            }
        return {"found": False, "message": "No registration found."}

    except Exception as e:
        print(f"Supabase lookup error: {e}")
        return {"found": False, "message": "Lookup failed due to a server error."}


def register_student(phone_number: str, name: str, student_class: str, email: str) -> dict:
    """
    Inserts a student registration into Supabase.
    Returns a dict describing success/failure, meant to be fed back to the LLM.
    """
    # Strict format validation -- rejects missing fields AND hallucinated/
    # placeholder values like "[phone]" or "N/A" that a truthy-check would miss
    errors = _validate_fields(phone_number, name, student_class, email)
    if errors:
        return {
            "success": False,
            "message": (
                "Cannot register yet, the following fields are invalid or missing: "
                + "; ".join(errors)
                + ". Ask the user for correct values before trying again."
            ),
        }

    cleaned_phone = re.sub(r"[\s\-()]", "", phone_number)

    client = get_supabase_client()
    try:
        existing = client.table("students").select("id").eq("phone_number", cleaned_phone).execute()
        if existing.data:
            return {
                "success": False,
                "already_registered": True,
                "message": "A student is already registered with this phone number.",
            }

        result = client.table("students").insert({
            "phone_number": cleaned_phone,
            "name": name.strip(),
            "class": student_class.strip(),
            "email": email.strip(),
        }).execute()

        if result.data:
            return {"success": True, "message": "Student registered successfully."}
        return {"success": False, "message": "Insert returned no data."}

    except Exception as e:
        print(f"Supabase insert error: {e}")
        if "duplicate key" in str(e).lower() or "unique" in str(e).lower():
            return {
                "success": False,
                "already_registered": True,
                "message": "A student is already registered with this phone number.",
            }
        return {"success": False, "message": f"Registration failed: {str(e)}"}