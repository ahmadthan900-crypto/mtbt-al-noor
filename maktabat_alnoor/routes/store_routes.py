import json
from pathlib import Path
from uuid import uuid4
from werkzeug.utils import secure_filename
from flask import Blueprint, request, jsonify, session, current_app
from database import get_db, read_site_settings
from auth import api_error, current_user

store_bp = Blueprint("store", __name__)

def book_dict(row):
    return {k: row[k] for k in row.keys()}

@store_bp.get("/books")
def books():
    db = get_db()
    search = (request.args.get("search") or "").strip()[:100]
    category = (request.args.get("category") or "").strip()[:60]
    sort = request.args.get("sort", "newest")
    page = max(1, min(int(request.args.get("page", 1) or 1), 10000))
    limit = max(1, min(int(request.args.get("limit", 20) or 20), 50))
    where, params = ["active = 1"], []
    if search:
        where.append("(title LIKE ? OR author LIKE ? OR description LIKE ?)")
        params.extend([f"%{search}%", f"%{search}%", f"%{search}%"])
    if category:
        where.append("category = ?")
        params.append(category)
    order = {"price_asc": "price ASC", "price_desc": "price DESC", "best": "sales DESC", "newest": "id DESC"}.get(sort, "id DESC")
    clause = " AND ".join(where)
    total = db.execute(f"SELECT COUNT(*) FROM books WHERE {clause}", params).fetchone()[0]
    rows = db.execute(f"SELECT * FROM books WHERE {clause} ORDER BY {order} LIMIT ? OFFSET ?", (*params, limit, (page-1)*limit)).fetchall()
    return jsonify({"success": True, "items": [book_dict(r) for r in rows], "pagination": {"page": page, "limit": limit, "total": total, "pages": (total+limit-1)//limit}})

@store_bp.get("/books/best-sellers")
def best_sellers():
    period = request.args.get("period", "all")
    rows = get_db().execute("SELECT * FROM books WHERE active=1 ORDER BY sales DESC LIMIT 12").fetchall()
    return jsonify({"success": True, "period": period, "items": [book_dict(r) for r in rows]})

@store_bp.get("/books/<int:book_id>")
def book_detail(book_id):
    row = get_db().execute("SELECT * FROM books WHERE id=? AND active=1", (book_id,)).fetchone()
    if not row:
        return api_error("BOOK_NOT_FOUND", "الكتاب غير موجود", 404)
    return jsonify({"success": True, "book": book_dict(row)})

@store_bp.get("/categories")
def categories():
    rows = get_db().execute("SELECT category AS name, COUNT(*) AS book_count FROM books WHERE active=1 GROUP BY category ORDER BY category").fetchall()
    return jsonify({"success": True, "items": [dict(r) for r in rows]})

@store_bp.get("/categories/<int:category_id>/books")
def category_books(category_id):
    # Compatibility route: categories are text labels in this starter schema.
    return api_error("CATEGORY_NOT_FOUND", "استخدم اسم القسم عبر ?category=اسم القسم في /api/v1/books", 404)

@store_bp.get("/cart")
def cart_get():
    cart = session.get("cart", {})
    db = get_db()
    items, total = [], 0
    for book_id, quantity in cart.items():
        row = db.execute("SELECT id,title,price,image,stock FROM books WHERE id=? AND active=1", (int(book_id),)).fetchone()
        if row:
            q = max(1, min(int(quantity), 50))
            item_total = row["price"] * q
            total += item_total
            items.append({**dict(row), "quantity": q, "subtotal": round(item_total, 2)})
    return jsonify({"success": True, "items": items, "total": round(total, 2)})

@store_bp.post("/cart/add")
def cart_add():
    data = request.get_json(silent=True) or {}
    try:
        book_id, quantity = int(data.get("book_id")), int(data.get("quantity", 1))
    except (TypeError, ValueError):
        return api_error("INVALID_INPUT", "بيانات الكتاب غير صحيحة")
    if quantity < 1 or quantity > 50:
        return api_error("INVALID_QUANTITY", "الكمية يجب أن تكون بين 1 و50")
    row = get_db().execute("SELECT id,stock FROM books WHERE id=? AND active=1", (book_id,)).fetchone()
    if not row:
        return api_error("BOOK_NOT_FOUND", "الكتاب غير موجود", 404)
    cart = session.get("cart", {})
    new_q = int(cart.get(str(book_id), 0)) + quantity
    if new_q > min(row["stock"], 50):
        return api_error("OUT_OF_STOCK", "الكمية المطلوبة غير متوفرة", 400)
    cart[str(book_id)] = new_q
    session["cart"] = cart
    session.modified = True
    return jsonify({"success": True, "message": "أُضيف الكتاب إلى السلة", "cart_count": sum(cart.values())}), 201

@store_bp.patch("/cart/item/<int:book_id>")
def cart_update(book_id):
    data = request.get_json(silent=True) or {}
    try: quantity = int(data.get("quantity"))
    except (TypeError, ValueError): return api_error("INVALID_QUANTITY", "أدخل كمية صحيحة")
    if quantity < 1 or quantity > 50: return api_error("INVALID_QUANTITY", "الكمية يجب أن تكون بين 1 و50")
    row = get_db().execute("SELECT stock FROM books WHERE id=? AND active=1", (book_id,)).fetchone()
    if not row: return api_error("BOOK_NOT_FOUND", "الكتاب غير موجود", 404)
    if quantity > row["stock"]: return api_error("OUT_OF_STOCK", "الكمية المطلوبة غير متوفرة")
    cart = session.get("cart", {})
    if str(book_id) not in cart: return api_error("CART_ITEM_NOT_FOUND", "العنصر غير موجود في السلة", 404)
    cart[str(book_id)] = quantity; session["cart"] = cart
    return jsonify({"success": True})

@store_bp.delete("/cart/item/<int:book_id>")
def cart_delete(book_id):
    cart = session.get("cart", {})
    cart.pop(str(book_id), None); session["cart"] = cart
    return jsonify({"success": True, "message": "تم حذف العنصر"})

@store_bp.delete("/cart/clear")
def cart_clear():
    session["cart"] = {}
    return jsonify({"success": True, "message": "تم تفريغ السلة"})

@store_bp.get("/ads")
def ads():
    settings = read_site_settings(get_db())
    items = []
    if settings.get("announcement_enabled") == "1" and settings.get("announcement_text", "").strip():
        items.append({"id": 1, "title": settings["announcement_text"], "subtitle": "", "image": "", "active": True})
    return jsonify({"success": True, "items": items})

@store_bp.get("/payment/sham-cash-info")
def sham_cash_info():
    settings = read_site_settings(get_db())
    enabled = settings.get("sham_cash_enabled") == "1"
    return jsonify({"success": True, "available": enabled,
        "name": settings.get("sham_cash_name", ""),
        "number": settings.get("sham_cash_number", ""),
        "note": settings.get("sham_cash_note", ""),
        "image": settings.get("sham_cash_image", ""),
        "message": "شام كاش غير متاح حالياً." if not enabled else "اتبع تعليمات التحويل الموضحة أدناه."})

@store_bp.post("/coupons/validate")
def coupon_validate():
    data = request.get_json(silent=True) or {}
    code = (data.get("code") or "").strip().upper()
    # Demo coupon, intended to be replaced with a database-backed admin-managed coupon table.
    if code == "SAVE10":
        cart = session.get("cart", {})
        db = get_db()
        total = 0
        for bid, qty in cart.items():
            row = db.execute("SELECT price FROM books WHERE id=?", (int(bid),)).fetchone()
            if row: total += row["price"] * int(qty)
        return jsonify({"success": True, "valid": True, "discount_percent": 10, "discount": round(total*0.1,2), "total_after_discount": round(total*0.9,2)})
    return jsonify({"success": True, "valid": False, "message": "الكوبون غير صالح"})

@store_bp.post("/orders")
def create_order():
    user = current_user()
    if not user: return api_error("UNAUTHORIZED", "سجّل الدخول قبل تأكيد الطلب", 401)
    is_form = bool(request.form)
    data = request.form if is_form else (request.get_json(silent=True) or {})
    method = data.get("payment_method", "")
    if method not in ("sham_cash", "cod"): return api_error("INVALID_PAYMENT_METHOD", "اختر طريقة دفع صحيحة")
    customer_name = (data.get("customer_name") or user["name"] or "").strip()[:120]
    customer_phone = (data.get("customer_phone") or user["phone"] or "").strip()[:30]
    payment_note = (data.get("payment_note") or "").strip()[:500]
    if not customer_name: return api_error("NAME_REQUIRED", "أدخل اسم صاحب الطلب")
    if not customer_phone: return api_error("PHONE_REQUIRED", "أدخل رقم هاتف للتواصل")
    settings = read_site_settings(get_db())
    if method == "sham_cash" and settings.get("sham_cash_enabled") != "1":
        return api_error("PAYMENT_NOT_CONFIGURED", "الدفع عبر شام كاش غير مفعّل حالياً. اختر الدفع عند الاستلام.", 400)
    proof = request.files.get("payment_proof") if is_form else None
    proof_path = ""
    if method == "sham_cash":
        if not proof or not proof.filename:
            return api_error("PROOF_REQUIRED", "ارفع صورة إثبات تحويل شام كاش قبل تأكيد الطلب")
        ext = Path(secure_filename(proof.filename)).suffix.lower()
        if ext not in {".png", ".jpg", ".jpeg", ".webp"}:
            return api_error("INVALID_PROOF_TYPE", "صيغة صورة الإثبات يجب أن تكون PNG أو JPG أو WEBP")
        upload_dir = Path(current_app.config["UPLOAD_FOLDER"]) / "payment_proofs"
        upload_dir.mkdir(parents=True, exist_ok=True)
        filename = f"proof_{uuid4().hex}{ext}"
        proof.save(upload_dir / filename)
        proof_path = f"/static/uploads/payment_proofs/{filename}"
    cart = session.get("cart", {})
    if not cart: return api_error("EMPTY_CART", "السلة فارغة")
    db = get_db()
    order_items, total = [], 0
    for bid, qty in cart.items():
        row = db.execute("SELECT id,title,price,stock FROM books WHERE id=? AND active=1", (int(bid),)).fetchone()
        if not row or int(qty) > row["stock"]: return api_error("STOCK_CHANGED", "تغير المخزون؛ راجع السلة")
        order_items.append({"book_id": row["id"], "title": row["title"], "quantity": int(qty), "price": row["price"]})
        total += row["price"] * int(qty)
    status = "payment_review" if method == "sham_cash" else "preparing"
    cur = db.execute("""INSERT INTO orders
        (user_id, items_json, total, payment_method, status, customer_name, customer_phone, payment_note, payment_proof)
        VALUES (?,?,?,?,?,?,?,?,?)""",
        (user["id"], json.dumps(order_items, ensure_ascii=False), round(total,2), method, status,
         customer_name, customer_phone, payment_note, proof_path))
    for item in order_items:
        db.execute("UPDATE books SET stock=stock-?, sales=sales+? WHERE id=?", (item["quantity"], item["quantity"], item["book_id"]))
    db.commit(); session["cart"] = {}
    return jsonify({"success": True, "order_id": cur.lastrowid, "tracking_url": f"/track/{cur.lastrowid}", "status": status}), 201

@store_bp.get("/orders")
def my_orders():
    user = current_user()
    if not user: return api_error("UNAUTHORIZED", "سجّل الدخول أولاً", 401)
    rows = get_db().execute("SELECT id,total,payment_method,status,created_at FROM orders WHERE user_id=? ORDER BY id DESC", (user["id"],)).fetchall()
    return jsonify({"success": True, "items": [dict(r) for r in rows]})

@store_bp.get("/orders/<int:order_id>")
def order_detail(order_id):
    user = current_user()
    if not user: return api_error("UNAUTHORIZED", "سجّل الدخول أولاً", 401)
    row = get_db().execute("SELECT * FROM orders WHERE id=? AND user_id=?", (order_id, user["id"])).fetchone()
    if not row: return api_error("ORDER_NOT_FOUND", "الطلب غير موجود", 404)
    data = dict(row); data["items"] = json.loads(data.pop("items_json"))
    return jsonify({"success": True, "order": data})

@store_bp.post("/orders/<int:order_id>/confirm-receipt")
def confirm_receipt(order_id):
    user = current_user()
    if not user: return api_error("UNAUTHORIZED", "سجّل الدخول أولاً", 401)
    data = request.get_json(silent=True) or {}
    if not isinstance(data.get("received"), bool): return api_error("INVALID_INPUT", "أرسل received بقيمة true أو false")
    db = get_db()
    row = db.execute("SELECT id FROM orders WHERE id=? AND user_id=?", (order_id, user["id"])).fetchone()
    if not row: return api_error("ORDER_NOT_FOUND", "الطلب غير موجود", 404)
    if data["received"]:
        db.execute("UPDATE orders SET status='received' WHERE id=?", (order_id,)); db.commit()
        return jsonify({"success": True, "message": "شكراً لتأكيد الاستلام"})
    return jsonify({"success": True, "message": "تم تسجيل ملاحظتك التجريبية؛ يلزم إضافة نظام تنبيهات الإدارة"})
