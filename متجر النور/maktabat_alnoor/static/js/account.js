document.addEventListener("DOMContentLoaded", async () => {
  const message = document.getElementById("accountMessage");
  const details = document.getElementById("accountDetails");
  try {
    const data = await apiFetch("/auth/me");
    document.getElementById("accountName").textContent = data.user.name || "";
    document.getElementById("accountPhone").textContent = data.user.phone || "";
    document.getElementById("accountRole").textContent = data.user.is_admin ? "مدير" : "مستخدم";
    message.textContent = "تم تسجيل الدخول بنجاح.";
    details.hidden = false;
  } catch (error) {
    message.textContent = "لم نعثر على جلسة تسجيل دخول فعّالة. سجّل الدخول أو أنشئ حسابًا للمتابعة.";
    const link = document.createElement("a");
    link.href = "/login";
    link.className = "btn btn-primary";
    link.textContent = "تسجيل الدخول";
    link.style.display = "inline-block";
    link.style.marginTop = "16px";
    message.insertAdjacentElement("afterend", link);
  }

  document.getElementById("logoutButton").addEventListener("click", async () => {
    const button = document.getElementById("logoutButton");
    button.disabled = true;
    try {
      await apiFetch("/auth/logout", {method: "POST"});
      location.href = "/login";
    } catch (error) {
      message.textContent = error.message || "تعذر تسجيل الخروج.";
      button.disabled = false;
    }
  });
});
