# مكتبة النور — API v1

Base path: `/api/v1`. جميع الاستجابات JSON. أخطاء API القياسية:
```json
{"success": false, "error": {"code": "INVALID_INPUT", "message": "رسالة عربية"}}
```

## المصادقة
- `POST /auth/request-otp` JSON: `{"name":"أحمد علي","phone":"+963912345678"}`. يطلب رمزاً تجريبياً.
- `POST /auth/verify-otp` JSON: `{"phone":"+963912345678","otp":"12345"}`. ينشئ/يدخل المستخدم.
- `POST /auth/logout` ينهي الجلسة.
- `GET /auth/me` يعيد المستخدم الحالي، أو 401.

> تحذير: OTP في النسخة التجريبية يظهر في طرفية الخادم؛ لا تستخدم هذه الآلية للإنتاج. اربط خدمة واتساب مستقلة حقيقية، وتخزين OTP مناسباً، وحدود محاولات، وحماية CSRF قبل النشر.

## الكتب والأقسام
- `GET /books?category=روايات&search=أرض&sort=price_asc&page=1&limit=20`
- `GET /books/{id}`
- `GET /books/best-sellers?period=all`
- `GET /categories`
- `GET /categories/{id}/books` غير مفعّل في هذه النسخة؛ الأقسام ممثلة بأسماء نصية ويُستخدم `/books?category=اسم القسم`.

## السلة
- `GET /cart`
- `POST /cart/add` JSON: `{"book_id":1,"quantity":2}`
- `PATCH /cart/item/{book_id}` JSON: `{"quantity":3}`
- `DELETE /cart/item/{book_id}`
- `DELETE /cart/clear`

## الكوبونات والطلبات
- `POST /coupons/validate` JSON: `{"code":"SAVE10"}` (كوبون تجريبي ثابت).
- `POST /orders` JSON: `{"payment_method":"cod"}` ويتطلب تسجيل الدخول. شام كاش غير مفعّل.
- `GET /orders` و`GET /orders/{id}` تتطلبان تسجيل الدخول، والطلب مرئي لصاحبه فقط.
- `POST /orders/{id}/confirm-receipt` JSON: `{"received":true}`.

## الإعلانات والدفع
- `GET /ads` يعيد إعلاناً تجريبياً.
- `GET /payment/sham-cash-info` يوضح أن إعداد شام كاش لم يكتمل.

## الإدارة (تتطلب is_admin=true)
- `GET /admin/books?search=...`
- `POST /admin/books` JSON: `{"title":"كتاب","author":"مؤلف","price":5,"category":"روايات","stock":10}`
- `PATCH /admin/books/{id}` JSON بالحقول المراد تعديلها.
- `DELETE /admin/books/{id}` يخفي الكتاب بدلاً من حذف سجله.
- `GET /admin/orders?status=preparing`
- `PATCH /admin/orders/{id}/status` JSON: `{"status":"delivering"}`.
- `GET /admin/stats/sales`
- `GET /admin/stats/best-sellers?period=all`
- `GET /admin/stats/orders-by-status`
- `GET /admin/users`
- `PATCH /admin/users/{id}/block` JSON: `{"blocked":true}`.

## حالات HTTP
`200` نجاح، `201` إنشاء، `400` مدخلات غير صالحة، `401` غير مسجل، `403` غير مخول، `404` غير موجود، `429` تجاوز الحد، `500` خطأ داخلي.

## قبل النشر الحقيقي
هذه نسخة بداية قابلة للتشغيل وليست نظام تجارة إلكترونية إنتاجياً كاملاً. قبل نشرها:
1. طبّق CSRF token فعلياً على جميع POST/PATCH/DELETE، مع فحص Origin/Referer عند الحاجة.
2. استبدل OTP التجريبي بخدمة واتساب خاصة على loopback مع مفتاح سري وPlaywright أو مزود رسمي، ولا تسجّل OTP في السجلات.
3. أضف نظام كوبونات/إعلانات/إعدادات دفع/تنبيهات بجداول إدارية فعلية؛ بعض المسارات حالياً تجريبية أو غير مطبقة.
4. أضف رفع ملفات آمن مع allowlist وفحص المحتوى وتخزين إثباتات الدفع خارج مجلد public، وإدارة المخزون والمعاملات.
5. استخدم HTTPS و`COOKIE_SECURE=1`، ومفتاح `SECRET_KEY` عشوائي، وWSGI server مثل Gunicorn خلف reverse proxy.
6. أنشئ حساب المدير من قاعدة البيانات يدوياً، ولا توجد بيانات دخول افتراضية.


## دخول المدير وإعدادات الموقع
- `POST /api/v1/auth/admin-login` — JSON: `{ "name": "...", "number": "...", "code": "..." }`
- `GET /api/v1/admin/settings` — قراءة نصوص الموقع (مدير فقط).
- `PATCH /api/v1/admin/settings` — تعديل العبارات والشعار والإعلان (مدير فقط).
