// =========================================================
// register.js - create a Staff account
// Sends the form to the backend: POST /api/auth/register
// The backend always makes the new user a "Staff".
// (Admin accounts are made with: python -m backend.create_admin)
// =========================================================

var form = document.getElementById("registerForm");
var errorBox = document.getElementById("registerError");
var showPassBtn = document.getElementById("showPass");
var submitBtn = form.querySelector("button[type=submit]");

// If user is already logged in, go to dashboard
if (localStorage.getItem("vs_token")) {
  window.location.href = "dashboard.html";
}

// Show / hide both password boxes
showPassBtn.addEventListener("click", function () {
  var first = document.getElementById("password");
  var second = document.getElementById("confirmPassword");
  var hide = first.type === "password";

  first.type = hide ? "text" : "password";
  second.type = hide ? "text" : "password";
  showPassBtn.innerHTML = hide ? '<i class="bi bi-eye-slash"></i>' : '<i class="bi bi-eye"></i>';
});

function showError(message) {
  errorBox.style.display = "block";
  errorBox.textContent = message;
  errorBox.scrollIntoView({ block: "nearest" });
}

// Same rules as the backend (the backend checks again, this only gives a faster answer)
function checkPassword(password) {
  if (password.length < 8) {
    return "Password must have at least 8 characters";
  }
  if (password.length > 72) {
    return "Password is too long (maximum 72 characters)";
  }
  if (!/[A-Za-z]/.test(password) || !/[0-9]/.test(password)) {
    return "Password must contain at least one letter and one number";
  }
  return "";
}

form.addEventListener("submit", function (e) {
  e.preventDefault();
  errorBox.style.display = "none";

  var name = document.getElementById("name").value.trim();
  var email = document.getElementById("email").value.trim();
  var password = document.getElementById("password").value;
  var confirmPassword = document.getElementById("confirmPassword").value;

  if (name.length < 2) {
    showError("Please enter your full name");
    return;
  }
  if (email === "") {
    showError("Please enter your email address");
    return;
  }
  var problem = checkPassword(password);
  if (problem !== "") {
    showError(problem);
    return;
  }
  if (password !== confirmPassword) {
    showError("Passwords do not match");
    return;
  }

  submitBtn.disabled = true;
  submitBtn.textContent = "Please wait...";

  api("POST", "/api/auth/register", { name: name, email: email, password: password })
    .then(function (data) {
      // the backend logs the new user in, so we save the token and open the dashboard
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
      showError(message);
      submitBtn.disabled = false;
      submitBtn.textContent = "Create account";
    });
});
