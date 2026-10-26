import sqlite3
from pathlib import Path
from flask import current_app, g

def get_db():
    if "db" not in g:
        Path(current_app.config["DATABASE"]).parent.mkdir(parents=True, exist_ok=True)
        g.db = sqlite3.connect(current_app.config["DATABASE"])
        g.db.row_factory = sqlite3.Row
        g.db.execute("PRAGMA foreign_keys = ON")
    return g.db

def close_db(_=None):
    db = g.pop("db", None)
    if db is not None:
        db.close()

DEFAULT_SETTINGS = {
    "logo_text": "ن", "site_name": "مكتبة النور", "brand_tagline": "رفيق رحلتك مع الكتب",
    "footer_tagline": "كلمات تضيء الطريق", "footer_description": "مساحة هادئة لاكتشاف كتابك القادم.", "footer_books_link": "تصفّح الكتب", "footer_cart_link": "سلة المشتريات", "footer_login_link": "تسجيل الدخول",
    "nav_home": "الرئيسية", "nav_books": "الكتب", "nav_categories": "الأقسام", "nav_about": "عن المكتبة", "nav_account": "حسابي", "nav_cart": "السلة",
    "hero_eyebrow": "لكل حكاية بداية", "hero_title": "افتح كتاباً،\nوافتح عالماً.", "hero_description": "كتب تلهمك، وحكايات ترافقك، وأفكار تستحق أن تكتشفها. اختر قراءتك القادمة من مكتبة النور.",
    "hero_art_line1": "وقتٌ لنفسك", "hero_art_line2": "وكتابٌ تحبّه",
    "hero_primary_button": "اكتشف الكتب", "hero_secondary_button": "تعرّف على اختياراتنا", "hero_proof_title": "كل يوم فرصة لقراءة جديدة", "hero_proof_subtitle": "ابدأ رحلتك من هنا",
    "benefit1_title": "كتب منتقاة", "benefit1_text": "خيارات تناسب شغفك", "benefit2_title": "تجربة سهلة", "benefit2_text": "تصفّح واطلب ببساطة", "benefit3_title": "قراءة تلهمك", "benefit3_text": "أفكار تبقى معك", "benefit4_title": "خيارات دفع", "benefit4_text": "بحسب إعدادات المتجر",
    "categories_eyebrow": "تصفّح حسب اهتمامك", "categories_title": "لكل قارئ حكايته", "category1_title": "روايات", "category1_text": "عوالم لا تنتهي", "category2_title": "تطوير الذات", "category2_text": "خطوات نحو الأفضل", "category3_title": "أدب وفكر", "category3_text": "كلمات تترك أثراً", "category4_title": "ثقافة ومعرفة", "category4_text": "اكتشف ما لا تعرفه",
    "featured_eyebrow": "اختيرت بعناية", "featured_title": "كتب تستحق وقتك", "featured_description": "اقتراحات صغيرة قد تفتح لك أبواباً كبيرة.", "featured_link": "اكتشف المجموعة كاملة",
    "newsletter_eyebrow": "مرحباً بك في مكتبتنا", "newsletter_title": "بعض الصفحات تغيّر كل شيء.", "newsletter_description": "امنح نفسك مساحة للمعرفة والخيال، ودع الكتاب المناسب يجد طريقه إليك.", "newsletter_button": "ابدأ التصفّح",
    "books_banner_eyebrow": "مساحة اكتشافك", "books_banner_title": "رفوف مليئة بالاحتمالات.", "books_banner_description": "ابحث عن كتاب يلامس اهتمامك أو تصفّح مجموعتنا.", "books_search_placeholder": "ابحث عن عنوان أو مؤلف…",
    "login_eyebrow": "أهلاً بعودتك", "login_title": "كل قراءة تبدأ بخطوة.", "login_description": "ادخل إلى حسابك لمتابعة طلباتك والعودة إلى كتبك المفضلة.", "login_form_heading": "أنشئ حسابك أو سجّل الدخول", "login_form_description": "سنرسل رمز تحقق إلى رقم هاتفك السوري.", "login_name_label": "الاسم بالعربية", "login_phone_label": "رقم الهاتف", "login_send_button": "إرسال رمز التحقق", "login_otp_label": "رمز التحقق (5 أرقام)", "login_verify_button": "تحقق ودخول", "login_fine_print": "في النسخة الحالية رمز التحقق تجريبي يظهر في طرفية الخادم. إرسال واتساب الحقيقي يحتاج إعداد الخدمة المستقلة.",
    "about_title": "عن مكتبة النور", "copyright_text": "© 2026 مكتبة النور — جميع الحقوق محفوظة",
    "announcement_text": "", "announcement_enabled": "0", "logo_image": "",
    "sham_cash_enabled": "0", "sham_cash_name": "", "sham_cash_number": "", "sham_cash_note": "", "sham_cash_image": ""
}

def init_db():
    from config import Config
    Path(Config.DATABASE).parent.mkdir(parents=True, exist_ok=True)
    db = sqlite3.connect(Config.DATABASE)
    settings_table_existed = db.execute("SELECT 1 FROM sqlite_master WHERE type='table' AND name='site_settings'").fetchone() is not None
    db.executescript("""
    PRAGMA foreign_keys = ON;
    CREATE TABLE IF NOT EXISTS users (
      id INTEGER PRIMARY KEY AUTOINCREMENT,
      name TEXT NOT NULL,
      phone TEXT NOT NULL UNIQUE,
      is_admin INTEGER NOT NULL DEFAULT 0,
      blocked INTEGER NOT NULL DEFAULT 0,
      created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
    );
    CREATE TABLE IF NOT EXISTS books (
      id INTEGER PRIMARY KEY AUTOINCREMENT,
      title TEXT NOT NULL,
      author TEXT NOT NULL,
      description TEXT NOT NULL DEFAULT '',
      price REAL NOT NULL CHECK(price >= 0),
      category TEXT NOT NULL DEFAULT 'روايات',
      image TEXT NOT NULL DEFAULT '',
      stock INTEGER NOT NULL DEFAULT 10 CHECK(stock >= 0),
      sales INTEGER NOT NULL DEFAULT 0,
      active INTEGER NOT NULL DEFAULT 1,
      created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
    );
    CREATE TABLE IF NOT EXISTS orders (
      id INTEGER PRIMARY KEY AUTOINCREMENT,
      user_id INTEGER NOT NULL,
      items_json TEXT NOT NULL,
      total REAL NOT NULL,
      payment_method TEXT NOT NULL,
      status TEXT NOT NULL DEFAULT 'preparing',
      customer_name TEXT NOT NULL DEFAULT '',
      customer_phone TEXT NOT NULL DEFAULT '',
      payment_note TEXT NOT NULL DEFAULT '',
      payment_proof TEXT NOT NULL DEFAULT '',
      created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
      FOREIGN KEY(user_id) REFERENCES users(id)
    );
    CREATE TABLE IF NOT EXISTS site_settings (
      key TEXT PRIMARY KEY,
      value TEXT NOT NULL DEFAULT ''
    );
    """)
    # Migrate databases created by earlier versions without deleting existing customer data.
    order_columns = {row[1] for row in db.execute("PRAGMA table_info(orders)").fetchall()}
    for column, definition in {
        "customer_name": "TEXT NOT NULL DEFAULT ''",
        "customer_phone": "TEXT NOT NULL DEFAULT ''",
        "payment_note": "TEXT NOT NULL DEFAULT ''",
        "payment_proof": "TEXT NOT NULL DEFAULT ''",
    }.items():
        if column not in order_columns:
            db.execute(f"ALTER TABLE orders ADD COLUMN {column} {definition}")
    # Ensure the previous release's built-in demo books never remain in the store.
    db.execute("DELETE FROM books WHERE (title,author) IN ((?,?),(?,?),(?,?),(?,?),(?,?),(?,?),(?,?),(?,?))", ("أرض زيكولا","عمرو عبد الحميد", "قواعد العشق الأربعون","إليف شافاق", "العادات الذرية","جيمس كلير", "فن اللامبالاة","مارك مانسون", "رسائل من القرآن","أدهم شرقاوي", "مئة عام من العزلة","غابرييل غارسيا ماركيز", "الأب الغني والأب الفقير","روبرت كيوساكي", "مقدمة ابن خلدون","ابن خلدون"))
    db.executemany("INSERT OR IGNORE INTO site_settings (key,value) VALUES (?,?)", DEFAULT_SETTINGS.items())
    db.commit()
    db.close()


def read_site_settings(db):
    values = dict(DEFAULT_SETTINGS)
    try:
        values.update({row["key"]: row["value"] for row in db.execute("SELECT key,value FROM site_settings")})
    except sqlite3.Error:
        pass
    return values
