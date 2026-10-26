from flask import Blueprint, request, jsonify, current_app
from pathlib import Path
from uuid import uuid4
from werkzeug.utils import secure_filename
from database import get_db
from auth import admin_required, api_error
from database import DEFAULT_SETTINGS

admin_bp = Blueprint("admin", __name__)

@admin_bp.get("/books")
@admin_required
def admin_books():
    search = (request.args.get("search") or "").strip()[:100]
    rows = get_db().execute("SELECT * FROM books WHERE title LIKE ? OR author LIKE ? ORDER BY id DESC", (f"%{search}%", f"%{search}%")).fetchall()
    return jsonify({"success": True, "items": [dict(r) for r in rows]})

@admin_bp.post("/books")
@admin_required
def add_book():
    data = request.get_json(silent=True) or {}
    title, author = (data.get("title") or "").strip(), (data.get("author") or "").strip()
    try: price = float(data.get("price"))
    except (TypeError, ValueError): return api_error("INVALID_PRICE", "أدخل سعراً صحيحاً")
    if not title or len(title) > 160 or not author or len(author) > 120 or price < 0:
        return api_error("INVALID_BOOK", "تحقق من عنوان الكتاب والمؤلف والسعر")
    db = get_db()
    cur = db.execute("INSERT INTO books (title,author,description,price,category,image,stock) VALUES (?,?,?,?,?,?,?)",
      (title, author, str(data.get("description",""))[:2000], price, str(data.get("category","روايات"))[:60], str(data.get("image",""))[:500], max(0,min(int(data.get("stock",10)),10000))))
    db.commit()
    return jsonify({"success": True, "id": cur.lastrowid}), 201

@admin_bp.patch("/books/<int:book_id>")
@admin_required
def edit_book(book_id):
    data = request.get_json(silent=True) or {}
    allowed = {"title","author","description","price","category","image","stock","active"}
    fields = {k:v for k,v in data.items() if k in allowed}
    if not fields: return api_error("EMPTY_UPDATE", "لا توجد بيانات للتعديل")
    if "price" in fields:
        try: fields["price"] = float(fields["price"])
        except (TypeError,ValueError): return api_error("INVALID_PRICE", "السعر غير صحيح")
        if fields["price"] < 0: return api_error("INVALID_PRICE", "السعر لا يمكن أن يكون سالباً")
    sql = ", ".join(f"{key}=?" for key in fields)
    db = get_db()
    cur = db.execute(f"UPDATE books SET {sql} WHERE id=?", (*fields.values(), book_id))
    db.commit()
    if not cur.rowcount: return api_error("BOOK_NOT_FOUND", "الكتاب غير موجود", 404)
    return jsonify({"success": True})

@admin_bp.delete("/books/<int:book_id>")
@admin_required
def delete_book(book_id):
    db = get_db()
    cur = db.execute("UPDATE books SET active=0 WHERE id=?", (book_id,))
    db.commit()
    if not cur.rowcount: return api_error("BOOK_NOT_FOUND", "الكتاب غير موجود", 404)
    return jsonify({"success": True, "message": "تم إخفاء الكتاب من المتجر"})

@admin_bp.get("/orders")
@admin_required
def admin_orders():
    status = (request.args.get("status") or "").strip()
    if status:
        rows = get_db().execute("SELECT o.*,COALESCE(NULLIF(o.customer_name,''),u.name) AS name,COALESCE(NULLIF(o.customer_phone,''),u.phone) AS phone FROM orders o JOIN users u ON u.id=o.user_id WHERE o.status=? ORDER BY o.id DESC", (status,)).fetchall()
    else:
        rows = get_db().execute("SELECT o.*,COALESCE(NULLIF(o.customer_name,''),u.name) AS name,COALESCE(NULLIF(o.customer_phone,''),u.phone) AS phone FROM orders o JOIN users u ON u.id=o.user_id ORDER BY o.id DESC").fetchall()
    return jsonify({"success": True, "items": [dict(r) for r in rows]})

@admin_bp.patch("/orders/<int:order_id>/status")
@admin_required
def update_order_status(order_id):
    data = request.get_json(silent=True) or {}
    status = data.get("status")
    allowed = {"payment_review","preparing","delivering","received"}
    if status not in allowed: return api_error("INVALID_STATUS", "حالة الطلب غير صالحة")
    db = get_db()
    cur = db.execute("UPDATE orders SET status=? WHERE id=?", (status, order_id)); db.commit()
    if not cur.rowcount: return api_error("ORDER_NOT_FOUND", "الطلب غير موجود", 404)
    return jsonify({"success": True})

@admin_bp.get("/stats/sales")
@admin_required
def sales_stats():
    row = get_db().execute("SELECT COUNT(*) AS orders_count, COALESCE(SUM(total),0) AS revenue FROM orders").fetchone()
    return jsonify({"success": True, "stats": dict(row)})

@admin_bp.get("/stats/best-sellers")
@admin_required
def best_stats():
    rows = get_db().execute("SELECT id,title,sales FROM books ORDER BY sales DESC LIMIT 10").fetchall()
    return jsonify({"success": True, "items": [dict(r) for r in rows]})

@admin_bp.get("/stats/orders-by-status")
@admin_required
def status_stats():
    rows = get_db().execute("SELECT status,COUNT(*) AS count FROM orders GROUP BY status").fetchall()
    return jsonify({"success": True, "items": [dict(r) for r in rows]})

@admin_bp.get("/users")
@admin_required
def users():
    rows = get_db().execute("SELECT id,name,phone,is_admin,blocked,created_at FROM users ORDER BY id DESC").fetchall()
    return jsonify({"success": True, "items": [dict(r) for r in rows]})

@admin_bp.patch("/users/<int:user_id>/block")
@admin_required
def block_user(user_id):
    data = request.get_json(silent=True) or {}
    blocked = data.get("blocked", True)
    if not isinstance(blocked, bool): return api_error("INVALID_INPUT", "blocked يجب أن تكون true أو false")
    db = get_db(); cur = db.execute("UPDATE users SET blocked=? WHERE id=?", (int(blocked), user_id)); db.commit()
    if not cur.rowcount: return api_error("USER_NOT_FOUND", "المستخدم غير موجود", 404)
    return jsonify({"success": True})



@admin_bp.post("/upload-payment-image")
@admin_required
def upload_payment_image():
    uploaded = request.files.get("image")
    if not uploaded or not uploaded.filename:
        return api_error("MISSING_IMAGE", "اختر صورة أولاً")
    original = secure_filename(uploaded.filename)
    suffix = Path(original).suffix.lower()
    if suffix not in {".png", ".jpg", ".jpeg", ".webp", ".gif"}:
        return api_error("INVALID_IMAGE_TYPE", "الأنواع المسموحة: PNG أو JPG أو WEBP أو GIF")
    folder = Path(current_app.config["UPLOAD_FOLDER"])
    folder.mkdir(parents=True, exist_ok=True)
    filename = f"sham-cash-{uuid4().hex}{suffix}"
    uploaded.save(folder / filename)
    return jsonify({"success": True, "url": f"/static/uploads/{filename}"}), 201

@admin_bp.get("/settings")
@admin_required
def get_settings():
    rows = get_db().execute("SELECT key,value FROM site_settings ORDER BY key").fetchall()
    values = dict(DEFAULT_SETTINGS)
    values.update({r["key"]: r["value"] for r in rows})
    return jsonify({"success": True, "settings": values})

@admin_bp.patch("/settings")
@admin_required
def update_settings():
    data = request.get_json(silent=True) or {}
    allowed = set(DEFAULT_SETTINGS.keys())
    updates = {str(k): str(v)[:3000] for k,v in data.items() if k in allowed and isinstance(v, (str,int,float,bool))}
    if not updates:
        return api_error("EMPTY_UPDATE", "لم يتم إرسال إعدادات صالحة")
    db = get_db()
    db.executemany("INSERT INTO site_settings (key,value) VALUES (?,?) ON CONFLICT(key) DO UPDATE SET value=excluded.value", updates.items())
    db.commit()
    return jsonify({"success": True, "message": "تم حفظ إعدادات الموقع والعبارات والشعار"})
