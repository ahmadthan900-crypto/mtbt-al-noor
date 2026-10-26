const API = "/api/v1";
async function apiFetch(path, options = {}) {
  const headers = new Headers(options.headers || {});
  if (options.body && !(options.body instanceof FormData) && !headers.has("Content-Type")) headers.set("Content-Type", "application/json");
  const response = await fetch(API + path, {...options, headers, credentials:"same-origin"});
  let data;
  try { data = await response.json(); } catch { data = {success:false,error:{message:"استجابة غير مفهومة من الخادم"}}; }
  if (!response.ok || data.success === false) throw new Error(data?.error?.message || "تعذر تنفيذ الطلب");
  return data;
}
function money(value){ return `${Number(value || 0).toFixed(2)} $`; }
function escapeHTML(value){ return String(value ?? "").replace(/[&<>"']/g, ch => ({"&":"&amp;","<":"&lt;",">":"&gt;",'"':"&quot;","'":"&#39;"}[ch])); }
function toast(message){ const el=document.getElementById("toast"); if(!el)return; el.textContent=message;el.classList.add("show");clearTimeout(window.__toastTimer);window.__toastTimer=setTimeout(()=>el.classList.remove("show"),2800); }
async function updateCartCount(){try{const data=await apiFetch("/cart");const el=document.getElementById("cartCount");if(el)el.textContent=data.items.reduce((sum,item)=>sum+item.quantity,0)}catch{}}
function bookCard(book){const image=book.image || "";return `<article class="book-card"><a href="/books?book=${book.id}" class="book-image" aria-label="عرض ${escapeHTML(book.title)}">${image?`<img loading="lazy" src="${escapeHTML(image)}" alt="غلاف ${escapeHTML(book.title)}" onerror="this.style.display='none'">`:`<span class="book-badge">مكتبة النور</span>`}<span class="book-badge">${escapeHTML(book.category)}</span></a><div class="book-info"><span class="book-category">${escapeHTML(book.category)}</span><h3 title="${escapeHTML(book.title)}">${escapeHTML(book.title)}</h3><p class="book-author">${escapeHTML(book.author)}</p><div class="book-bottom"><span class="book-price">${money(book.price)}</span><button class="add-cart" data-add="${book.id}" aria-label="إضافة ${escapeHTML(book.title)} إلى السلة">＋</button></div></div></article>`}
document.addEventListener("click", async e=>{const button=e.target.closest("[data-add]");if(button){button.disabled=true;try{await apiFetch("/cart/add",{method:"POST",body:JSON.stringify({book_id:Number(button.dataset.add),quantity:1})});toast("أُضيف الكتاب إلى السلة");await updateCartCount()}catch(err){toast(err.message)}finally{button.disabled=false}}});
const menuToggle=document.getElementById("menuToggle");if(menuToggle)menuToggle.addEventListener("click",()=>document.getElementById("mainNav")?.classList.toggle("open"));
document.addEventListener("DOMContentLoaded",updateCartCount);

// Show the account area as the signed-in user's account and avoid stale login links.
document.addEventListener("DOMContentLoaded", async () => {
  const label = document.getElementById("accountNavLabel");
  const link = document.getElementById("accountNavLink");
  if (!label || !link) return;
  try {
    const data = await apiFetch("/auth/me");
    if (data.user) { label.textContent = "معلومات الحساب"; link.title = "معلومات الحساب"; }
  } catch (_) {
    label.textContent = "تسجيل الدخول"; link.title = "تسجيل الدخول"; link.href = "/login";
  }
});
