from datetime import datetime
from uuid import uuid4

from flask import Blueprint, jsonify, request
from werkzeug.security import check_password_hash, generate_password_hash

from utils.auth_store import create_user, get_user_by_email

auth_bp = Blueprint("auth", __name__)

ALLOWED_ROLES = {"doctor", "admin", "patient"}


def _serialize_user(user_doc):
    return {
        "id": user_doc.get("user_id") or user_doc.get("_id"),
        "email": user_doc["email"],
        "name": user_doc["name"],
        "role": user_doc["role"],
    }


@auth_bp.route("/auth/register", methods=["POST"])
def register():
    data = request.get_json(silent=True) or {}
    email = (data.get("email") or "").lower().strip()
    password = data.get("password") or ""
    name = (data.get("name") or "").strip()
    role = (data.get("role") or "doctor").strip().lower()

    if not email or not password or not name:
        return jsonify({"success": False, "error": "All fields are required."}), 400
    if len(password) < 6:
        return jsonify({"success": False, "error": "Password must be at least 6 characters."}), 400
    if role not in ALLOWED_ROLES:
        return jsonify({"success": False, "error": "Invalid role selected."}), 400
    if get_user_by_email(email):
        return jsonify({"success": False, "error": "An account with this email already exists."}), 409

    created_user = create_user({
        "user_id": f"usr_{uuid4().hex[:12]}",
        "email": email,
        "name": name,
        "role": role,
        "password_hash": generate_password_hash(password),
        "created_at": datetime.utcnow().isoformat(),
    })

    return jsonify({"success": True, "user": _serialize_user(created_user)}), 201


@auth_bp.route("/auth/login", methods=["POST"])
def login():
    data = request.get_json(silent=True) or {}
    email = (data.get("email") or "").lower().strip()
    password = data.get("password") or ""

    if not email or not password:
        return jsonify({"success": False, "error": "Email and password are required."}), 400

    user = get_user_by_email(email)
    if not user:
        return jsonify({"success": False, "error": "Account not found. Please register first."}), 404

    if not check_password_hash(user.get("password_hash", ""), password):
        return jsonify({"success": False, "error": "Incorrect password."}), 401

    return jsonify({"success": True, "user": _serialize_user(user)})
