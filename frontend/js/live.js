// =========================================================
// live.js - live camera monitoring page
//
// How it works:
//  1. "Start" sends POST /api/detection/start to the backend.
//  2. The backend (OpenCV + YOLO + tracker) processes the video and
//     sends back annotated frames as a stream (MJPEG).
//  3. We show that stream in an <img> tag and ask for the status
//     (FPS, counts) every second.
// =========================================================

var streamImg = document.getElementById("streamImg");
var placeholder = document.getElementById("placeholder");
var liveBadge = document.getElementById("liveBadge");
var statusTimer = null;

// ---------- Fill the source list (webcam + videos folder) ----------
function loadSources() {
  var select = document.getElementById("sourceSelect");
  var html = '<option value="0">Webcam (camera 0)</option>';

  api("GET", "/api/detection/videos").then(function (videos) {
    for (var i = 0; i < videos.length; i++) {
      html += '<option value="' + videos[i] + '">Video: ' + videos[i] + "</option>";
    }
    select.innerHTML = html;
  }).catch(function (error) {
    select.innerHTML = html;
    showServerError(error.message);
  });
}

// ---------- Show the live picture ----------
function showStream() {
  // the time in the URL stops the browser from using an old picture
  streamImg.src = API_URL + "/api/detection/stream?token=" + getToken() + "&t=" + Date.now();
  streamImg.style.display = "block";
  placeholder.style.display = "none";
  liveBadge.classList.add("on");
}

function hideStream() {
  streamImg.removeAttribute("src");
  streamImg.style.display = "none";
  placeholder.style.display = "block";
  liveBadge.classList.remove("on");
}

// ---------- Show counts + status ----------
function showStatus(status) {
  document.getElementById("cameraStatus").textContent = status.state;
  document.getElementById("fpsValue").textContent = status.fps;

  // one row for every class that YOLO sees
  var html = "";
  var total = 0;
  for (var label in status.counts) {
    html += '<div class="info-row"><span>' + label + "</span><span>" + status.counts[label] + "</span></div>";
    total += status.counts[label];
  }
  if (html === "") {
    html = '<p class="text-muted mb-0" style="font-size:14px">Nothing detected yet.</p>';
  }
  document.getElementById("countList").innerHTML = html;
  document.getElementById("countTotal").textContent = total;

  var messageBox = document.getElementById("statusMessage");
  if (status.message) {
    messageBox.style.display = "block";
    messageBox.textContent = status.message;
  } else {
    messageBox.style.display = "none";
  }

  // the process may have ended by itself (video finished, error)
  if (!status.running) {
    stopPolling();
    hideStream();
    document.getElementById("startBtn").disabled = false;
    document.getElementById("stopBtn").disabled = true;
  }
}

function checkStatus() {
  api("GET", "/api/detection/status").then(showStatus).catch(function () {});
}

function startPolling() {
  stopPolling();
  statusTimer = setInterval(checkStatus, 1000);
}

function stopPolling() {
  if (statusTimer) {
    clearInterval(statusTimer);
    statusTimer = null;
  }
}

// ---------- Start ----------
function startDetection() {
  var source = document.getElementById("sourceSelect").value;

  document.getElementById("startBtn").disabled = true;
  api("POST", "/api/detection/start", { source: source })
    .then(function () {
      document.getElementById("stopBtn").disabled = false;
      showStream();
      startPolling();
      showToast("Detection started");
    })
    .catch(function (error) {
      document.getElementById("startBtn").disabled = false;
      showToast(error.message);
    });
}

// ---------- Stop ----------
function stopDetection() {
  document.getElementById("stopBtn").disabled = true;
  api("POST", "/api/detection/stop")
    .then(function (status) {
      showStatus(status);
      showToast("Detection stopped");
    })
    .catch(function (error) {
      showToast(error.message);
    });
}

document.getElementById("startBtn").addEventListener("click", startDetection);
document.getElementById("stopBtn").addEventListener("click", stopDetection);

// When the page opens, check if the backend is already running detection
loadSources();
api("GET", "/api/detection/status").then(function (status) {
  showStatus(status);
  if (status.running) {
    document.getElementById("startBtn").disabled = true;
    document.getElementById("stopBtn").disabled = false;
    showStream();
    startPolling();
  }
}).catch(function (error) {
  showServerError(error.message);
});
