document.addEventListener("DOMContentLoaded", async () => {
  const items = document.getElementById("checkoutItems"), total = document.getElementById("checkoutTotal");
  const form = document.getElementById("checkoutForm"), message = document.getElementById("checkoutMessage");
  const shamOption = document.getElementById("shamCashOption"), shamRadio = form.querySelector('input[value="sham_cash"]');
  const codRadio = form.querySelector('input[value="cod"]'), shamInfo = document.getElementById("shamCashCustomerInfo");
  const proof = document.getElementById("paymentProof"), proofPreview = document.getElementById("proofPreview");
  function esc(value) { return String(value ?? "").replace(/[&<>"']/g, c => ({"&":"&amp;","<":"&lt;",">":"&gt;",'"':"&quot;","'":"&#39;"}[c])); }
  try {
    const data = await apiFetch("/cart");
    items.innerHTML = data.items.map(i => `<div class="checkout-book"><img src="${esc(i.image)}" alt=""><span>${esc(i.title)} × ${i.quantity}<b>${money(i.subtotal)}</b></span></div>`).join("") || '<p class="muted">السلة فارغة.</p>';
    total.textContent = money(data.total);
  } catch (e) { items.textContent = e.message; }
  let signedInUser = null;
  try {
    const me = await apiFetch("/auth/me");
    signedInUser = me.user || null;
    if (signedInUser) {
      const customerName = document.getElementById("customerName");
      const customerPhone = document.getElementById("customerPhone");
      customerName.value = signedInUser.name || customerName.value;
      customerPhone.value = signedInUser.phone || customerPhone.value;
      customerName.dataset.accountPrefilled = "1";
      customerPhone.dataset.accountPrefilled = "1";
    }
  } catch (_) {
    // The server still checks authentication when the customer confirms the order.
  }
  try {
    const info = await apiFetch("/payment/sham-cash-info");
    if (info.available) {
      shamRadio.disabled = false; shamOption.classList.remove("disabled-option");
      document.getElementById("shamCashShortNote").textContent = "متاح — راجع بيانات التحويل أدناه.";
      document.getElementById("shamCashBadge").textContent = "متاح";
      document.getElementById("shamCashCustomerName").textContent = info.name || "شام كاش";
      document.getElementById("shamCashCustomerNumber").textContent = info.number || "";
      document.getElementById("shamCashCustomerNote").textContent = info.note || "حوّل المبلغ إلى الحساب الموضح ثم ارفع صورة إثبات التحويل.";
      const image = document.getElementById("shamCashCustomerImage");
      image.innerHTML = info.image ? `<img src="${esc(info.image)}" alt="صورة حساب شام كاش أو رمز QR">` : '<span>▣</span><small>لم تُضف صورة للحساب</small>';
    }
  } catch (_) {}
  function updatePaymentUI() {
    const selected = shamRadio.checked && !shamRadio.disabled;
    shamInfo.hidden = !selected;
    proof.required = selected;
  }
  shamRadio.addEventListener("change", updatePaymentUI);
  codRadio.addEventListener("change", updatePaymentUI);
  updatePaymentUI();
  proof.addEventListener("change", () => {
    proofPreview.innerHTML = ""; proofPreview.hidden = true;
    const file = proof.files?.[0]; if (!file) return;
    if (!/^image\/(png|jpeg|webp)$/.test(file.type) || file.size > 5 * 1024 * 1024) {
      message.textContent = "اختر صورة PNG أو JPG أو WEBP بحجم لا يتجاوز 5 ميغابايت."; proof.value = ""; return;
    }
    const img = document.createElement("img"); img.alt = "معاينة إثبات التحويل"; img.src = URL.createObjectURL(file);
    proofPreview.append(img); proofPreview.hidden = false; message.textContent = "";
  });
  form.addEventListener("submit", async e => {
    e.preventDefault(); message.textContent = "جارٍ تأكيد الطلب…";
    const button = document.getElementById("submitOrderButton"); button.disabled = true;
    try {
      try { const me = await apiFetch("/auth/me"); if (!me.user) throw new Error("سجّل الدخول أولاً"); }
      catch { throw new Error("يرجى تسجيل الدخول أولاً قبل تأكيد الطلب."); }
      const body = new FormData(form);
      const result = await apiFetch("/orders", {method:"POST", body});
      message.innerHTML = `تم إنشاء الطلب رقم <b>#${Number(result.order_id)}</b>. جارٍ فتح صفحة التتبع…`;
      await updateCartCount();
      window.location.href = result.tracking_url || `/track/${result.order_id}`;
    } catch (err) { message.textContent = err.message; button.disabled = false; }
  });
});
