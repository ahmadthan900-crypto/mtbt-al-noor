import re, secrets, time
from flask import Blueprint, request, jsonify, session
from database import get_db
from flask import current_app
from auth import api_error, current_user

auth_bp = Blueprint("auth", __name__)
# Demo OTP only. Real WhatsApp sending must be integrated before production.
OTP_STORE = {}
OTP_LIMIT = {}

def valid_phone(phone):
    return bool(re.fullmatch(r"\+9639\d{8}", phone or ""))

def valid_name(name):
    return bool(name and len(name.strip()) <= 60 and re.fullmatch(r"[\u0600-\u06FF\sـ]+", name.strip()))


@auth_bp.post("/admin-login")
def admin_login():
    data = request.get_json(silent=True) or {}
    name = (data.get("name") or "").strip()
    number = (data.get("number") or "").strip()
    code = (data.get("code") or "").strip()
    expected = current_app.config
    valid = (secrets.compare_digest(name, str(expected["ADMIN_NAME"])) and
             secrets.compare_digest(number, str(expected["ADMIN_NUMBER"])) and
             secrets.compare_digest(code, str(expected["ADMIN_CODE"])))
    if not valid:
        return api_error("INVALID_ADMIN_LOGIN", "بيانات دخول المدير غير صحيحة", 401)
    db = get_db()
    user = db.execute("SELECT id FROM users WHERE phone=?", (number,)).fetchone()
    if user:
        db.execute("UPDATE users SET name=?,is_admin=1,blocked=0 WHERE id=?", (name, user["id"]))
        user_id = user["id"]
    else:
        cur = db.execute("INSERT INTO users (name,phone,is_admin) VALUES (?,?,1)", (name, number))
        user_id = cur.lastrowid
    db.commit()
    session.clear()
    session["user_id"] = user_id
    session["admin_authenticated"] = True
    session.permanent = True
    return jsonify({"success": True, "message": "تم تسجيل دخول المدير", "redirect": "/admin"})

@auth_bp.post("/request-otp")
def request_otp():
    data = request.get_json(silent=True) or {}
    name, phone = (data.get("name") or "").strip(), (data.get("phone") or "").strip()
    if not valid_name(name):
        return api_error("INVALID_NAME", "أدخل اسماً عربياً صحيحاً")
    if not valid_phone(phone):
        return api_error("INVALID_PHONE", "أدخل رقم هاتف سوري بصيغة +9639xxxxxxxx")
    key = (request.remote_addr or "unknown", phone)
    now = time.time()
    if now - OTP_LIMIT.get(key, 0) < 60:
        return api_error("RATE_LIMITED", "انتظر دقيقة قبل طلب رمز جديد", 429)
    OTP_LIMIT[key] = now
    otp = f"{secrets.randbelow(100000):05d}"
    OTP_STORE[phone] = {"otp": otp, "name": name, "expires": now + 300}
    # Development only: OTP is logged in server terminal, not returned to browser.
    print(f"[DEMO OTP] {phone}: {otp} (integrate private WhatsApp microservice for production)")
    return jsonify({"success": True, "message": "تم إنشاء رمز تجريبي. راجع طرفية الخادم؛ إرسال واتساب الحقيقي غير مفعّل بعد."})

@auth_bp.post("/verify-otp")
def verify_otp():
    data = request.get_json(silent=True) or {}
    phone, otp = (data.get("phone") or "").strip(), (data.get("otp") or "").strip()
    record = OTP_STORE.get(phone)
    if not record or record["expires"] < time.time() or not secrets.compare_digest(record["otp"], otp):
        return api_error("INVALID_OTP", "رمز التحقق غير صحيح أو انتهت صلاحيته", 400)
    db = get_db()
    user = db.execute("SELECT id, name, phone, is_admin, blocked FROM users WHERE phone = ?", (phone,)).fetchone()
    if user and user["blocked"]:
        return api_error("ACCOUNT_BLOCKED", "هذا الحساب محظور", 403)
    if not user:
        cur = db.execute("INSERT INTO users (name, phone) VALUES (?, ?)", (record["name"], phone))
        db.commit()
        user = db.execute("SELECT id, name, phone, is_admin, blocked FROM users WHERE id = ?", (cur.lastrowid,)).fetchone()
    session.clear()
    session["user_id"] = user["id"]
    session.permanent = True
    session.modified = True
    OTP_STORE.pop(phone, None)
    return jsonify({"success": True, "user": {"id": user["id"], "name": user["name"], "phone": user["phone"], "is_admin": bool(user["is_admin"])}})

@auth_bp.post("/logout")
def logout():
    session.clear()
    return jsonify({"success": True, "message": "تم تسجيل الخروج"})

@auth_bp.get("/me")
def me():
    user = current_user()
    if not user:
        return api_error("UNAUTHORIZED", "لست مسجلاً الدخول", 401)
    return jsonify({"success": True, "user": {"id": user["id"], "name": user["name"], "phone": user["phone"], "is_admin": bool(user["is_admin"])}})
