document.addEventListener("DOMContentLoaded", async () => {
  const labels = {payment_review:"قيد مراجعة الدفع", preparing:"قيد التجهيز", delivering:"قيد التوصيل", received:"تم الاستلام"};
  const sequence = ["payment_review", "preparing", "delivering", "received"];
  const message = document.getElementById("trackingMessage");
  try {
    const data = await apiFetch(`/orders/${Number(window.TRACKING_ORDER_ID)}`), order = data.order;
    document.getElementById("trackingOrderNumber").textContent = `#${order.id}`;
    const badge = document.getElementById("trackingStatusBadge"); badge.textContent = labels[order.status] || order.status; badge.dataset.status = order.status;
    const index = sequence.indexOf(order.status);
    document.getElementById("trackingSteps").innerHTML = sequence.map((status, i) => `<div class="tracking-step ${i <= index ? "complete" : ""} ${status === order.status ? "current" : ""}"><span>${i < index ? "✓" : i + 1}</span><b>${labels[status]}</b>${status === "payment_review" ? "<small>التحقق من إثبات التحويل</small>" : ""}</div>`).join("");
    const items = (order.items || []).map(item => `<li>${escapeHTML(item.title)} × ${Number(item.quantity)}</li>`).join("");
    const proof = order.payment_proof ? `<p><b>إثبات التحويل:</b> <a href="${escapeHTML(order.payment_proof)}" target="_blank" rel="noopener">عرض الصورة المرفوعة</a></p>` : "";
    document.getElementById("trackingDetails").innerHTML = `<p><b>صاحب الطلب:</b> ${escapeHTML(order.customer_name || "")}</p><p><b>رقم الهاتف:</b> ${escapeHTML(order.customer_phone || "")}</p><p><b>طريقة الدفع:</b> ${order.payment_method === "sham_cash" ? "شام كاش" : "الدفع عند الاستلام"}</p><p><b>الإجمالي:</b> ${money(order.total)}</p><p><b>تاريخ الطلب:</b> ${escapeHTML(order.created_at || "")}</p>${order.payment_note ? `<p><b>ملاحظتك للدفع:</b> ${escapeHTML(order.payment_note)}</p>` : ""}${proof}<ul>${items}</ul>`;
    message.textContent = order.status === "payment_review" ? "استلمنا طلبك وإثبات التحويل، وهو بانتظار مراجعة المتجر." : "هذه أحدث حالة مسجلة لطلبك.";
  } catch (err) {
    message.textContent = err.message.includes("سجّل الدخول") ? "سجّل الدخول بالحساب الذي أنشأت منه الطلب لمتابعة حالته." : err.message;
    document.getElementById("trackingSteps").innerHTML = "";
  }
});
