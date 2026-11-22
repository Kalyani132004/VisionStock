// =========================================================
// login.js - login page
// Sends the email and password to the backend: POST /api/auth/login
// The backend returns a token. We keep the token in localStorage
// and send it with every other request (see api() in data.js).
// =========================================================

var form = document.getElementById("loginForm");
var errorBox = document.getElementById("loginError");
var showPassBtn = document.getElementById("showPass");
var loginBtn = form.querySelector("button[type=submit]");

// If user is already logged in, go to dashboard
if (localStorage.getItem("vs_token")) {
  window.location.href = "dashboard.html";
}

// Show / hide password
showPassBtn.addEventListener("click", function () {
  var passInput = document.getElementById("password");
  if (passInput.type === "password") {
    passInput.type = "text";
    showPassBtn.innerHTML = '<i class="bi bi-eye-slash"></i>';
  } else {
    passInput.type = "password";
    showPassBtn.innerHTML = '<i class="bi bi-eye"></i>';
  }
});

form.addEventListener("submit", function (e) {
  e.preventDefault();

  var email = document.getElementById("email").value.trim();
  var password = document.getElementById("password").value;

  errorBox.style.display = "none";
  loginBtn.disabled = true;
  loginBtn.textContent = "Please wait...";

  api("POST", "/api/auth/login", { email: email, password: password })
    .then(function (data) {
      // save token and user (never save the password)
      localStorage.setItem("vs_token", data.access_token);
      localStorage.setItem("vs_user", JSON.stringify({
        name: data.user.name,
        role: data.user.role
      }));
      window.location.href = "dashboard.html";
    })
    .catch(function (error) {
      var message = error.message;
      if (message === "Failed to fetch") {
        message = "Cannot connect to the backend. Please start the server first.";
      }
      errorBox.style.display = "block";
      errorBox.textContent = message;
      loginBtn.disabled = false;
      loginBtn.textContent = "Login";
    });
});
