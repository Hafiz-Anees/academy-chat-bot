"""Shared in-memory state: sessions, locks, and dedup tracking."""
import asyncio

# {session_id: [{"role":..., "content":...}]}
sessions: dict[str, list] = {}

# WhatsApp message IDs already processed (guards against Meta's webhook retries)
processed_message_ids: set[str] = set()

# One asyncio.Lock per user, so their messages are handled in order, never concurrently
_user_locks: dict[str, asyncio.Lock] = {}


def get_user_lock(user_id: str) -> asyncio.Lock:
    if user_id not in _user_locks:
        _user_locks[user_id] = asyncio.Lock()
    return _user_locks[user_id]