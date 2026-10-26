from flask import Flask, render_template, jsonify, request, session
from config import Config
from database import init_db, get_db, read_site_settings
from routes.auth_routes import auth_bp
from routes.store_routes import store_bp
from routes.admin_routes import admin_bp

app = Flask(__name__)
app.config.from_object(Config)

init_db()
app.register_blueprint(auth_bp, url_prefix="/api/v1/auth")
app.register_blueprint(store_bp, url_prefix="/api/v1")
app.register_blueprint(admin_bp, url_prefix="/api/v1/admin")

@app.context_processor
def inject_site_settings():
    try:
        return {"site": read_site_settings(get_db())}
    except Exception:
        return {"site": {}}

@app.get("/")
def home():
    return render_template("index.html")

@app.get("/books")
def books_page():
    return render_template("books.html")

@app.get("/cart")
def cart_page():
    return render_template("cart.html")

@app.get("/checkout")
def checkout_page():
    return render_template("checkout.html")

@app.get("/login")
def login_page():
    return render_template("login.html")

@app.get("/account")
def account_page():
    return render_template("account.html")

@app.get("/track/<int:order_id>")
def track_order_page(order_id):
    return render_template("tracking.html", order_id=order_id)

@app.get("/admin")
def admin_page():
    return render_template("admin.html")

@app.errorhandler(404)
def not_found(_):
    if request.path.startswith("/api/"):
        return jsonify({"success": False, "error": {"code": "NOT_FOUND", "message": "المسار غير موجود"}}), 404
    return render_template("404.html"), 404

@app.errorhandler(500)
def server_error(_):
    if request.path.startswith("/api/"):
        return jsonify({"success": False, "error": {"code": "SERVER_ERROR", "message": "حدث خطأ داخلي"}}), 500
    return render_template("404.html"), 500

if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5000, debug=False)
