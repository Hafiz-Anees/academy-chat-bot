"""LangChain tool definitions for the admissions agent."""
from langchain_core.tools import tool
from core.database import get_supabase_client

@tool
def register_student(phone_number: str, name: str, student_class: str, email: str) -> dict:
    """
    Inserts a student registration into Supabase.
    Returns a dict describing success/failure, meant to be fed back to the LLM.
    """
    # Validate all fields are present and non-empty before touching the DB
    fields = {"phone_number": phone_number, "name": name, "student_class": student_class, "email": email}
    missing = [k for k, v in fields.items() if not v or not str(v).strip()]
    if missing:
        return {"success": False, "message": f"Missing required fields: {', '.join(missing)}."}

    client = get_supabase_client()
    try:
        # Check for an existing registration under this phone number first
        existing = client.table("students").select("id").eq("phone_number", phone_number).execute()
        if existing.data:
            return {
                "success": False,
                "already_registered": True,
                "message": "A student is already registered with this phone number.",
            }

        result = client.table("students").insert({
            "phone_number": phone_number,
            "name": name,
            "class": student_class,
            "email": email,
        }).execute()

        if result.data:
            return {"success": True, "message": "Student registered successfully."}
        return {"success": False, "message": "Insert returned no data."}

    except Exception as e:
        print(f"Supabase insert error: {e}")
        # Unique constraint violation (belt-and-suspenders vs. the DB-level constraint)
        if "duplicate key" in str(e).lower() or "unique" in str(e).lower():
            return {
                "success": False,
                "already_registered": True,
                "message": "A student is already registered with this phone number.",
            }
        return {"success": False, "message": f"Registration failed: {str(e)}"}

@tool
def check_registration(email: str = None) -> str:
    """
    Check whether a student is already registered. Use this when a user asks to
    see, check, or confirm their registration status.

    On WhatsApp, you do NOT need to ask for anything — the system will
    automatically look up the registration using the user's WhatsApp number.
    Only ask the user for their email if you are on website chat (no phone
    number is available in that context) AND the automatic lookup was not used.

    Never ask the user to provide someone else's contact info to check a
    registration on their behalf.

    Args:
        email: The email address to look up (only needed on website chat).
    """
    pass


REGISTRATION_TOOLS = [register_student, check_registration]