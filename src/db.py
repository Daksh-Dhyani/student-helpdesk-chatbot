"""Small helper for talking to Supabase over its REST interface."""
import datetime as dt

import requests
import streamlit as st

TIMEOUT = 15


class DBError(Exception):
    """Raised when the database cannot be reached or refuses a request."""


def _config():
    cfg = st.secrets["supabase"]
    return cfg["url"].rstrip("/"), cfg["key"]


def db_ready():
    """True if the Supabase settings exist in secrets."""
    try:
        _config()
        return True
    except Exception:
        return False


def _call(method, path, params=None, body=None, prefer=None):
    base, key = _config()
    headers = {"apikey": key, "Content-Type": "application/json"}
    if key.startswith("eyJ"):
        headers["Authorization"] = "Bearer " + key
    if prefer:
        headers["Prefer"] = prefer
    try:
        r = requests.request(
            method, base + "/rest/v1/" + path,
            headers=headers, params=params, json=body, timeout=TIMEOUT,
        )
    except requests.RequestException as e:
        raise DBError("network error: " + type(e).__name__) from None
    if not r.ok:
        raise DBError(f"database error {r.status_code}")
    if not r.text:
        return None
    return r.json()


def list_conversations(email, limit=30):
    """Newest first: id, title, updated_at."""
    return _call("GET", "conversations", params={
        "select": "id,title,updated_at",
        "user_email": f"eq.{email}",
        "order": "updated_at.desc",
        "limit": limit,
    }) or []


def load_conversation(email, conversation_id):
    rows = _call("GET", "conversations", params={
        "select": "id,title,messages",
        "id": f"eq.{conversation_id}",
        "user_email": f"eq.{email}",
        "limit": 1,
    }) or []
    return rows[0] if rows else None


def save_conversation(email, conversation_id, title, messages):
    """Create (conversation_id=None) or update a chat. Returns its id."""
    if conversation_id:
        _call("PATCH", "conversations", params={
            "id": f"eq.{conversation_id}",
            "user_email": f"eq.{email}",
        }, body={
            "title": title,
            "messages": messages,
            "updated_at": dt.datetime.now(dt.timezone.utc).isoformat(),
        }, prefer="return=minimal")
        return conversation_id
    rows = _call("POST", "conversations", body={
        "user_email": email, "title": title, "messages": messages,
    }, prefer="return=representation")
    return rows[0]["id"]


def delete_conversation(email, conversation_id):
    _call("DELETE", "conversations", params={
        "id": f"eq.{conversation_id}",
        "user_email": f"eq.{email}",
    }, prefer="return=minimal")


def delete_all_conversations(email):
    _call("DELETE", "conversations", params={
        "user_email": f"eq.{email}",
    }, prefer="return=minimal")


def bump_usage(day, key):
    """Add 1 to today's counter for key and return the new count."""
    return int(_call("POST", "rpc/bump_usage",
                     body={"p_day": day, "p_key": key}))


def get_usage(day, key):
    rows = _call("GET", "usage_log", params={
        "select": "count",
        "day": f"eq.{day}",
        "user_key": f"eq.{key}",
        "limit": 1,
    }) or []
    return rows[0]["count"] if rows else 0


def add_feedback(kind, message, contact, email):
    _call("POST", "feedback", body={
        "kind": kind, "message": message,
        "contact": contact, "user_email": email,
    }, prefer="return=minimal")