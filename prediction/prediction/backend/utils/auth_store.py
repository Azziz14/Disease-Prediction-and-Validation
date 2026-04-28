import json
import logging
from pathlib import Path
from typing import Any, Dict, Optional

from bson import ObjectId

from utils.db import db_client

logger = logging.getLogger(__name__)

AUTH_STORE_PATH = Path(__file__).resolve().parents[1] / "data" / "auth_users.json"


def _read_local_users() -> Dict[str, Dict[str, Any]]:
    if not AUTH_STORE_PATH.exists():
        return {}

    try:
        return json.loads(AUTH_STORE_PATH.read_text(encoding="utf-8"))
    except Exception as exc:
        logger.error("Failed to read local auth store: %s", exc)
        return {}


def _write_local_users(users: Dict[str, Dict[str, Any]]) -> None:
    AUTH_STORE_PATH.parent.mkdir(parents=True, exist_ok=True)
    AUTH_STORE_PATH.write_text(json.dumps(users, indent=2), encoding="utf-8")


def get_user_by_email(email: str) -> Optional[Dict[str, Any]]:
    email_key = email.lower().strip()

    if db_client.db is not None:
        user = db_client.db.users.find_one({"email": email_key})
        if not user:
            return None
        user["_id"] = str(user["_id"])
        return user

    users = _read_local_users()
    return users.get(email_key)


def create_user(user_doc: Dict[str, Any]) -> Dict[str, Any]:
    email_key = user_doc["email"].lower().strip()

    if db_client.db is not None:
        payload = dict(user_doc)
        insert_result = db_client.db.users.insert_one(payload)
        payload["_id"] = str(insert_result.inserted_id)
        return payload

    users = _read_local_users()
    payload = dict(user_doc)
    payload["_id"] = str(ObjectId())
    users[email_key] = payload
    _write_local_users(users)
    return payload


def ensure_default_admin() -> None:
    """Ensure default admin account exists."""
    admin_email = "admin@123"
    existing_admin = get_user_by_email(admin_email)
    
    if not existing_admin:
        from werkzeug.security import generate_password_hash
        admin_user = {
            "email": admin_email,
            "password_hash": generate_password_hash("admin123"),
            "name": "System Administrator",
            "role": "admin"
        }
        create_user(admin_user)
        logger.info(f"Created default admin account: {admin_email}")
    else:
        logger.info(f"Default admin account already exists: {admin_email}")
