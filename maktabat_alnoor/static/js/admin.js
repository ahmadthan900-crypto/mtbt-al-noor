document.addEventListener("DOMContentLoaded", () => {
  const loginPanel = document.getElementById("adminLoginPanel");
  const dashboard = document.getElementById("adminDashboard");
  const loginForm = document.getElementById("adminLoginForm");
  const loginMessage = document.getElementById("adminLoginMessage");
  const stats = document.getElementById("adminStats");
  const books = document.getElementById("adminBooks");
  const orders = document.getElementById("adminOrders");
  const message = document.getElementById("adminMessage");
  const pageTitles = {
    overview: ["نظرة عامة", "ملخص سريع لحالة مكتبتك."],
    orders: ["إدارة الطلبات", "راجع الطلبات وغيّر حالتها من مكان واحد."],
    books: ["إدارة الكتب", "أضف كتبك وتحكم بما يظهر في واجهة المتجر."],
    shamcash: ["إعدادات شام كاش", "إدارة بيانات الدفع والصورة والتعليمات المعروضة للزبائن."],
    appearance: ["الشكل والعبارات", "تحكم بالشعار والنصوص والإعلانات التي تظهر في المتجر."]
  };
  const editable = {
    site_name:"اسم المكتبة", logo_text:"الشعار النصي", logo_image:"رابط صورة الشعار", brand_tagline:"العبارة تحت الشعار",
    nav_home:"القائمة: الرئيسية", nav_books:"القائمة: الكتب", nav_categories:"القائمة: الأقسام", nav_about:"القائمة: عن المكتبة", nav_account:"القائمة: حسابي", nav_cart:"القائمة: السلة",
    hero_eyebrow:"عبارة أعلى الواجهة الرئيسية", hero_art_line1:"العبارة الفنية 1", hero_art_line2:"العبارة الفنية 2", hero_title:"العنوان الرئيسي (استخدم سطراً جديداً للفصل)", hero_description:"وصف الواجهة الرئيسية", hero_primary_button:"زر الواجهة الرئيسي", hero_secondary_button:"الرابط الثانوي", hero_proof_title:"العبارة الصغيرة في الواجهة", hero_proof_subtitle:"الوصف الصغير",
    benefit1_title:"ميزة 1: العنوان", benefit1_text:"ميزة 1: الوصف", benefit2_title:"ميزة 2: العنوان", benefit2_text:"ميزة 2: الوصف", benefit3_title:"ميزة 3: العنوان", benefit3_text:"ميزة 3: الوصف", benefit4_title:"ميزة 4: العنوان", benefit4_text:"ميزة 4: الوصف",
    categories_eyebrow:"عبارة قسم التصنيفات", categories_title:"عنوان قسم التصنيفات", category1_title:"القسم 1: العنوان", category1_text:"القسم 1: الوصف", category2_title:"القسم 2: العنوان", category2_text:"القسم 2: الوصف", category3_title:"القسم 3: العنوان", category3_text:"القسم 3: الوصف", category4_title:"القسم 4: العنوان", category4_text:"القسم 4: الوصف",
    featured_eyebrow:"عبارة قسم الكتب المميزة", featured_title:"عنوان قسم الكتب المميزة", featured_description:"وصف قسم الكتب المميزة", featured_link:"رابط عرض كل الكتب",
    newsletter_eyebrow:"عبارة القسم الختامي", newsletter_title:"عنوان القسم الختامي", newsletter_description:"وصف القسم الختامي", newsletter_button:"زر القسم الختامي",
    books_banner_eyebrow:"عبارة أعلى صفحة الكتب", books_banner_title:"عنوان صفحة الكتب", books_banner_description:"وصف صفحة الكتب", books_search_placeholder:"عبارة مربع البحث",
    login_eyebrow:"عبارة صفحة الدخول", login_title:"عنوان صفحة الدخول", login_description:"وصف صفحة الدخول", login_form_heading:"عنوان نموذج الدخول", login_form_description:"وصف نموذج الدخول", login_name_label:"تسمية حقل الاسم", login_phone_label:"تسمية حقل الهاتف", login_send_button:"زر إرسال رمز التحقق", login_otp_label:"تسمية حقل رمز التحقق", login_verify_button:"زر التحقق والدخول", login_fine_print:"ملاحظة أسفل نموذج الدخول",
    footer_tagline:"عبارة التذييل", footer_description:"وصف التذييل", footer_books_link:"رابط التذييل: الكتب", footer_cart_link:"رابط التذييل: السلة", footer_login_link:"رابط التذييل: الدخول", copyright_text:"عبارة حقوق النشر", announcement_text:"نص الإعلان العلوي", announcement_enabled:"إظهار الإعلان العلوي؟ (1 نعم / 0 لا)"
  };
  let currentSettings = {};

  function esc(value) { return String(value ?? "").replace(/[&<>"']/g, c => ({"&":"&amp;","<":"&lt;",">":"&gt;",'"':"&quot;","'":"&#39;"}[c])); }
  function showTab(name) {
    document.querySelectorAll("[data-admin-view]").forEach(p => p.classList.toggle("active", p.dataset.adminView === name));
    document.querySelectorAll("[data-admin-tab]").forEach(b => b.classList.toggle("active", b.dataset.adminTab === name));
    document.getElementById("adminPageTitle").textContent = pageTitles[name][0];
    document.getElementById("adminPageSubtitle").textContent = pageTitles[name][1];
    if (name === "shamcash") renderShamPreview();
    window.scrollTo({top: 0, behavior: "smooth"});
  }
  document.querySelectorAll("[data-admin-tab]").forEach(btn => btn.addEventListener("click", () => showTab(btn.dataset.adminTab)));

  function renderOrders(items) {
    const html = items.map(o => `<div class="admin-order-row"><span><b>طلب #${o.id} — ${esc(o.customer_name || o.name)}</b><small>${esc(o.customer_phone || o.phone || "")} · ${money(o.total)} · ${o.payment_method === "sham_cash" ? "شام كاش" : "الدفع عند الاستلام"}<br>${esc(o.created_at || "")}${o.payment_note ? `<br>ملاحظة الدفع: ${esc(o.payment_note)}` : ""}${o.payment_proof ? `<br><a href="${esc(o.payment_proof)}" target="_blank" rel="noopener">عرض إثبات التحويل</a>` : ""}</small></span><select aria-label="حالة الطلب ${o.id}" data-order-status="${o.id}"><option value="payment_review" ${o.status === "payment_review" ? "selected" : ""}>قيد مراجعة الدفع</option><option value="preparing" ${o.status === "preparing" ? "selected" : ""}>قيد التجهيز</option><option value="delivering" ${o.status === "delivering" ? "selected" : ""}>قيد التوصيل</option><option value="received" ${o.status === "received" ? "selected" : ""}>تم الاستلام</option></select></div>`).join("") || '<div class="admin-empty-state"><span>▤</span><b>لا توجد طلبات حتى الآن</b><small>ستظهر الطلبات هنا عندما يبدأ الزبائن بالشراء.</small></div>';
    orders.innerHTML = html;
    document.getElementById("overviewOrders").innerHTML = items.slice(0, 4).map(o => `<div class="admin-mini-order"><span class="admin-mini-order-icon">▤</span><span><b>طلب #${o.id}</b><small>${esc(o.name)} · ${o.payment_method === "sham_cash" ? "شام كاش" : "الدفع عند الاستلام"}</small></span><strong>${money(o.total)}</strong></div>`).join("") || '<div class="admin-empty-state compact"><span>✓</span><b>لا توجد طلبات جديدة</b><small>سيظهر ملخص الطلبات هنا.</small></div>';
    document.getElementById("ordersNavCount").textContent = items.length;
    document.getElementById("ordersCountPill").textContent = `${items.length} طلب`;
  }

  async function loadSettings() {
    const data = await apiFetch("/admin/settings");
    currentSettings = data.settings || {};
    const wrap = document.getElementById("settingsFields");
    wrap.innerHTML = Object.entries(editable).map(([key, label]) => {
      const value = currentSettings[key] ?? "";
      const area = /description|title|announcement_text|hero_title|fine_print|tagline/.test(key);
      const imageHint = key === "logo_image" ? '<small class="field-help">رابط مباشر لصورة الشعار، أو اتركه فارغاً للشعار النصي.</small>' : "";
      return `<label>${esc(label)}${area ? `<textarea name="${key}" rows="${["hero_description","newsletter_description","footer_description"].includes(key) ? 3 : 2}" maxlength="3000">${esc(value)}</textarea>` : `<input name="${key}" maxlength="3000" value="${esc(value)}" ${key === "announcement_enabled" ? 'inputmode="numeric"' : ""}>`}${imageHint}</label>`;
    }).join("");
    const enabled = document.getElementById("shamCashEnabled");
    enabled.checked = currentSettings.sham_cash_enabled === "1";
    const form = document.getElementById("shamCashForm");
    ["sham_cash_name", "sham_cash_number", "sham_cash_note", "sham_cash_image"].forEach(k => { const el = form.elements[k]; if (el) el.value = currentSettings[k] || ""; });
    renderShamPreview();
  }

  function renderShamPreview() {
    const form = document.getElementById("shamCashForm");
    if (!form) return;
    const name = form.elements.sham_cash_name.value.trim();
    const number = form.elements.sham_cash_number.value.trim();
    const note = form.elements.sham_cash_note.value.trim();
    const imageUrl = form.elements.sham_cash_image.value.trim();
    document.getElementById("shamCashNamePreview").textContent = name || "اسم صاحب الحساب";
    document.getElementById("shamCashNumberPreview").textContent = number || "رقم الحساب سيظهر هنا";
    document.getElementById("shamCashNotePreview").textContent = note || "ستظهر تعليمات الدفع هنا.";
    const box = document.getElementById("shamCashImagePreview");
    box.innerHTML = imageUrl ? `<img src="${esc(imageUrl)}" alt="معاينة صورة حساب شام كاش" onerror="this.remove();this.parentElement.innerHTML='<span>▣</span><small>تعذر تحميل الصورة، تحقق من الرابط</small>'">` : '<span>▣</span><small>ستظهر صورة الحساب هنا</small>';
    const state = document.getElementById("shamCashState");
    state.textContent = document.getElementById("shamCashEnabled").checked ? "مفعّل" : "غير مفعّل";
    state.classList.toggle("enabled", document.getElementById("shamCashEnabled").checked);
  }
  ["sham_cash_name", "sham_cash_number", "sham_cash_note", "sham_cash_image", "shamCashEnabled"].forEach(id => {
    const el = document.getElementById(id) || document.querySelector(`[name="${id}"]`);
    if (el) el.addEventListener("input", renderShamPreview);
  });
  document.getElementById("shamCashImageFile").addEventListener("change", async e => {
    const file = e.target.files[0]; if (!file) return;
    const status = document.getElementById("shamCashUploadMessage");
    if (file.size > 5 * 1024 * 1024) { status.textContent = "حجم الصورة أكبر من 5 ميغابايت."; e.target.value = ""; return; }
    const body = new FormData(); body.append("image", file); status.textContent = "جارٍ رفع الصورة…";
    try {
      const result = await apiFetch("/admin/upload-payment-image", {method:"POST", body});
      document.querySelector('#shamCashForm [name="sham_cash_image"]').value = new URL(result.url, window.location.origin).href;
      status.textContent = "تم رفع الصورة. احفظ إعدادات شام كاش لتثبيتها."; renderShamPreview();
    } catch (err) { status.textContent = err.message; }
  });

  async function load() {
    try {
      const [s, b, o] = await Promise.all([apiFetch("/admin/stats/sales"), apiFetch("/admin/books"), apiFetch("/admin/orders")]);
      stats.innerHTML = `<div class="stat-card"><small>إجمالي الطلبات</small><b>${s.stats.orders_count}</b></div><div class="stat-card"><small>قيمة المبيعات</small><b>${money(s.stats.revenue)}</b></div><div class="stat-card"><small>الكتب المنشورة</small><b>${b.items.filter(x => x.active !== 0).length}</b></div>`;
      books.innerHTML = b.items.filter(x => x.active !== 0).map(x => `<div class="admin-book-row"><span><b>${esc(x.title)}</b><small>${esc(x.author)} · ${money(x.price)} · الكمية: ${x.stock}</small></span><button class="btn btn-outline" data-delete-book="${x.id}">إخفاء</button></div>`).join("") || '<div class="admin-empty-state"><span>▥</span><b>المكتبة فارغة حالياً</b><small>أضف أول كتاب من النموذج الموجود على اليسار.</small></div>';
      renderOrders(o.items);
      await loadSettings();
    } catch (e) {
      stats.innerHTML = `<div class="notice-box">${esc(e.message)} — تأكد من تسجيل الدخول ببيانات المدير.</div>`;
    }
  }

  async function checkSession() {
    try { await apiFetch("/admin/settings"); loginPanel.hidden = true; dashboard.hidden = false; await load(); }
    catch { loginPanel.hidden = false; dashboard.hidden = true; }
  }
  loginForm.addEventListener("submit", async e => {
    e.preventDefault(); loginMessage.textContent = "جارٍ التحقق من بيانات المدير…";
    const data = Object.fromEntries(new FormData(loginForm).entries());
    try { await apiFetch("/auth/admin-login", {method:"POST", body:JSON.stringify(data)}); loginMessage.textContent = "تم الدخول بنجاح"; await checkSession(); }
    catch (err) { loginMessage.textContent = err.message; }
  });
  document.getElementById("reloadAdmin").addEventListener("click", load);
  document.getElementById("adminLogout").addEventListener("click", async () => {
    try { await apiFetch("/auth/logout", {method:"POST"}); }
    finally { loginPanel.hidden = false; dashboard.hidden = true; loginForm.reset(); loginMessage.textContent = "تم تسجيل الخروج"; }
  });
  document.getElementById("addBookForm").addEventListener("submit", async e => {
    e.preventDefault();
    const form = e.currentTarget;
    const button = form.querySelector('button[type="submit"]');
    const oldText = button.textContent;
    const data = Object.fromEntries(new FormData(form).entries());
    data.price = Number(data.price); data.stock = Number(data.stock || 0);
    button.disabled = true; button.textContent = "جارٍ إضافة الكتاب…";
    message.textContent = "يتم حفظ الكتاب…"; message.classList.remove("error-message");
    try {
      await apiFetch("/admin/books", {method:"POST", body:JSON.stringify(data)});
      message.textContent = "تمت إضافة الكتاب وحفظه بنجاح.";
      toast("تمت إضافة الكتاب"); form.reset(); await load();
    } catch (err) {
      message.textContent = "لم تتم إضافة الكتاب: " + (err?.message || "خطأ غير معروف");
      message.classList.add("error-message");
    } finally { button.disabled = false; button.textContent = oldText; }
  });
  async function submitWithFeedback(form, button, messageEl, successText, payloadFactory) {
    const oldText = button.textContent;
    button.disabled = true;
    button.textContent = "جارٍ الحفظ…";
    messageEl.textContent = "يتم إرسال التغييرات إلى الخادم…";
    messageEl.classList.remove("error-message");
    try {
      const payload = payloadFactory();
      const result = await apiFetch("/admin/settings", {method:"PATCH", body:JSON.stringify(payload)});
      if (!result || result.success !== true) throw new Error("لم يؤكد الخادم حفظ التغييرات.");
      messageEl.textContent = successText;
      toast(successText);
      return true;
    } catch (err) {
      messageEl.textContent = "لم يتم الحفظ: " + (err?.message || "خطأ غير معروف");
      messageEl.classList.add("error-message");
      return false;
    } finally {
      button.disabled = false;
      button.textContent = oldText;
    }
  }
  document.getElementById("siteSettingsForm").addEventListener("submit", async e => {
    e.preventDefault();
    const form = e.currentTarget;
    const button = form.querySelector('button[type="submit"]');
    const messageEl = document.getElementById("settingsMessage");
    await submitWithFeedback(form, button, messageEl, "تم حفظ إعدادات المتجر بنجاح.", () => Object.fromEntries(new FormData(form).entries()));
  });
  document.getElementById("shamCashForm").addEventListener("submit", async e => {
    e.preventDefault();
    const form = e.currentTarget;
    const button = form.querySelector('button[type="submit"]');
    const messageEl = document.getElementById("shamCashMessage");
    const ok = await submitWithFeedback(form, button, messageEl, "تم حفظ إعدادات شام كاش بنجاح.", () => {
      const data = Object.fromEntries(new FormData(form).entries());
      data.sham_cash_enabled = form.elements.sham_cash_enabled.checked ? "1" : "0";
      return data;
    });
    if (ok) renderShamPreview();
  });
  document.addEventListener("click", async e => {
    const b = e.target.closest("[data-delete-book]"); if (!b) return;
    if (!confirm("هل تريد إخفاء هذا الكتاب من المتجر؟")) return;
    try { await apiFetch("/admin/books/" + b.dataset.deleteBook, {method:"DELETE"}); await load(); }
    catch (err) { toast(err.message); }
  });
  document.addEventListener("change", async e => {
    const s = e.target.closest("[data-order-status]"); if (!s) return;
    try { await apiFetch("/admin/orders/" + s.dataset.orderStatus + "/status", {method:"PATCH", body:JSON.stringify({status:s.value})}); toast("تم تحديث حالة الطلب"); }
    catch (err) { toast(err.message); }
  });
  checkSession();
});
