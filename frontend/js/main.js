// =========================================================
// main.js - code shared by all pages
// (login check, sidebar, clock, logout, toast message)
// =========================================================

// ---------- 1. Login check ----------
// Pages that need login have data-protected="yes" on the <body> tag
function checkLogin() {
  var protectedPage = document.body.getAttribute("data-protected");
  var token = localStorage.getItem("vs_token");

  if (protectedPage === "yes" && !token) {
    window.location.href = "login.html";
  }
}

checkLogin();

// ---------- 2. Show user name in the top bar ----------
function showUser() {
  var user = JSON.parse(localStorage.getItem("vs_user") || "null");
  if (!user) {
    return;
  }

  var nameBox = document.getElementById("userName");
  var roleBox = document.getElementById("userRole");
  var avatar = document.getElementById("userAvatar");

  if (nameBox) { nameBox.textContent = user.name; }
  if (roleBox) { roleBox.textContent = user.role; }
  if (avatar) { avatar.textContent = user.name.charAt(0).toUpperCase(); }
}

// ---------- 3. Sidebar open / close on mobile ----------
function setupSidebar() {
  var sidebar = document.getElementById("sidebar");
  var overlay = document.getElementById("overlay");
  var toggleBtn = document.getElementById("menuToggle");

  if (!sidebar || !toggleBtn) {
    return;
  }

  toggleBtn.addEventListener("click", function () {
    sidebar.classList.toggle("open");
    overlay.classList.toggle("show");
  });

  // clicking the dark area closes the sidebar
  overlay.addEventListener("click", function () {
    sidebar.classList.remove("open");
    overlay.classList.remove("show");
  });
}

// ---------- 4. Live clock ----------
function updateClock() {
  var box = document.getElementById("clock");
  if (!box) {
    return;
  }
  var now = new Date();
  var dateText = now.toLocaleDateString("en-IN", {
    weekday: "short", day: "numeric", month: "short", year: "numeric"
  });
  var timeText = now.toLocaleTimeString("en-IN");
  box.innerHTML = dateText + "<br><strong>" + timeText + "</strong>";
}

// ---------- 5. Logout ----------
function logout() {
  localStorage.removeItem("vs_token");
  localStorage.removeItem("vs_user");
  window.location.href = "login.html";
}

// ---------- 6. Small toast message ----------
function showToast(message) {
  var toast = document.getElementById("toast");
  if (!toast) {
    return;
  }
  toast.textContent = message;
  toast.style.display = "block";

  setTimeout(function () {
    toast.style.display = "none";
  }, 2500);
}

// ---------- Run when page loads ----------
document.addEventListener("DOMContentLoaded", function () {
  showUser();
  setupSidebar();
  updateClock();
  setInterval(updateClock, 1000);

  var logoutBtn = document.getElementById("logoutBtn");
  if (logoutBtn) {
    logoutBtn.addEventListener("click", function (e) {
      e.preventDefault();
      logout();
    });
  }
});
