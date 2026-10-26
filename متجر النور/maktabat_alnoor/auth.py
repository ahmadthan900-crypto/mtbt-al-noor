from functools import wraps
from flask import session, jsonify
from database import get_db

def api_error(code, message, status=400):
    return jsonify({"success": False, "error": {"code": code, "message": message}}), status

def current_user():
    user_id = session.get("user_id")
    if not user_id:
        return None
    user = get_db().execute("SELECT id, name, phone, is_admin, blocked FROM users WHERE id = ?", (user_id,)).fetchone()
    if not user or user["blocked"]:
        session.clear()
        return None
    return user

def login_required(fn):
    @wraps(fn)
    def wrapper(*args, **kwargs):
        user = current_user()
        if not user:
            return api_error("UNAUTHORIZED", "يرجى تسجيل الدخول أولاً", 401)
        return fn(*args, **kwargs)
    return wrapper

def admin_required(fn):
    @wraps(fn)
    def wrapper(*args, **kwargs):
        user = current_user()
        if not user:
            return api_error("UNAUTHORIZED", "يرجى تسجيل الدخول أولاً", 401)
        if not user["is_admin"]:
            return api_error("FORBIDDEN", "هذه الصفحة مخصصة للمدير", 403)
        return fn(*args, **kwargs)
    return wrapper
