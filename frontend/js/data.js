// =========================================================
// data.js - talks to the FastAPI backend
//
//  - api()          : send a request to the backend
//  - loadAll()      : load products, shelves, inventory and events
//  - helper functions used by every page
//
// If you open the pages from http://127.0.0.1:8000 (served by FastAPI),
// the API is on the same address. If you open them with Live Server or
// by double click, we use http://127.0.0.1:8000 for the API.
// =========================================================

var API_URL = (location.port === "8000") ? "" : "http://127.0.0.1:8000";

// ---------- Data loaded from the backend ----------
var cache = { products: [], shelves: [], inventory: [], events: [] };

function getToken() {
  return localStorage.getItem("vs_token");
}

// ---------- 1. Send a request to the backend ----------
// method: "GET", "POST", "PUT", "DELETE"
// Returns a Promise with the JSON answer.
function api(method, path, body) {
  var options = {
    method: method,
    headers: { "Content-Type": "application/json" }
  };

  var token = getToken();
  if (token) {
    options.headers["Authorization"] = "Bearer " + token;
  }
  if (body) {
    options.body = JSON.stringify(body);
  }

  return fetch(API_URL + path, options).then(function (response) {
    // token expired or missing -> go to login
    if (response.status === 401 && path.indexOf("/api/auth/login") === -1) {
      localStorage.removeItem("vs_token");
      localStorage.removeItem("vs_user");
      window.location.href = "login.html";
      throw new Error("Please login again");
    }

    return response.json().catch(function () { return {}; }).then(function (data) {
      if (!response.ok) {
        throw new Error(getErrorText(data));
      }
      return data;
    });
  });
}

// FastAPI sends errors as {detail: "text"} or {detail: [ {msg: ...} ]}
function getErrorText(data) {
  if (data && typeof data.detail === "string") {
    return data.detail;
  }
  if (data && Array.isArray(data.detail) && data.detail.length > 0) {
    // pydantic starts its messages with "Value error, " - we remove that
    return String(data.detail[0].msg).replace("Value error, ", "");
  }
  return "Something went wrong";
}

// ---------- 2. Convert API data to the shape used by our pages ----------
function formatTime(text) {
  if (!text) {
    return "-";
  }
  return text.substring(0, 16).replace("T", " ");
}

function convertProduct(p) {
  return { id: p.product_id, name: p.product_name, category: p.category,
           minStock: p.minimum_stock, detectClass: p.detect_class || "" };
}

function convertShelf(s) {
  return { id: s.shelf_id, name: s.shelf_name, location: s.location, status: s.status,
           occupancy: s.occupancy, roiX: s.roi_x, roiY: s.roi_y, roiW: s.roi_w, roiH: s.roi_h };
}

function convertInventory(i) {
  return { id: i.inventory_id, productId: i.product_id, shelfId: i.shelf_id,
           qty: i.detected_quantity, updated: formatTime(i.updated_at) };
}

function convertEvent(e) {
  return { id: e.event_id, productId: e.product_id, shelfId: e.shelf_id,
           type: e.event_type, qty: e.quantity, time: formatTime(e.event_time) };
}

function mapList(list, converter) {
  var result = [];
  for (var i = 0; i < list.length; i++) {
    result.push(converter(list[i]));
  }
  return result;
}

// ---------- 3. Load everything from the backend ----------
// callback runs when the data is ready
function loadAll(callback) {
  Promise.all([
    api("GET", "/api/products"),
    api("GET", "/api/shelves"),
    api("GET", "/api/inventory"),
    api("GET", "/api/events?limit=200")
  ]).then(function (results) {
    cache.products = mapList(results[0], convertProduct);
    cache.shelves = mapList(results[1], convertShelf);
    cache.inventory = mapList(results[2], convertInventory);
    cache.events = mapList(results[3], convertEvent);
    hideServerError();
    callback();
  }).catch(function (error) {
    showServerError(error.message);
  });
}

// Same as loadAll (name makes the page code easier to read)
function onDataReady(callback) {
  loadAll(callback);
}

function getProducts() { return cache.products; }
function getShelves() { return cache.shelves; }
function getInventory() { return cache.inventory; }
function getEvents() { return cache.events; }

// ---------- 4. Error message when backend is not running ----------
function showServerError(message) {
  var box = document.getElementById("serverError");
  if (!box) {
    box = document.createElement("div");
    box.id = "serverError";
    box.className = "alert alert-danger";
    var content = document.querySelector(".page-content");
    if (content) {
      content.insertBefore(box, content.firstChild);
    }
  }
  if (message === "Failed to fetch") {
    message = "Cannot connect to the backend. Start it with:  uvicorn backend.main:app --reload";
  }
  box.textContent = message;
}

function hideServerError() {
  var box = document.getElementById("serverError");
  if (box) {
    box.remove();
  }
}

// ---------- 5. WebSocket for live updates ----------
// onMessage(message) is called when the backend sends an update.
// If the connection drops, we try again after 3 seconds.
function connectSocket(onMessage) {
  var base = API_URL === "" ? location.origin : API_URL;
  var url = base.replace("http", "ws") + "/ws/inventory?token=" + getToken();
  var socket = new WebSocket(url);

  socket.onmessage = function (event) {
    onMessage(JSON.parse(event.data));
  };

  socket.onclose = function () {
    if (getToken()) {
      setTimeout(function () { connectSocket(onMessage); }, 3000);
    }
  };
}

// ---------- 6. Helper functions ----------
function findProduct(id) {
  var list = cache.products;
  for (var i = 0; i < list.length; i++) {
    if (list[i].id == id) {
      return list[i];
    }
  }
  return { name: "Unknown", category: "-", minStock: 0 };
}

function findShelf(id) {
  var list = cache.shelves;
  for (var i = 0; i < list.length; i++) {
    if (list[i].id == id) {
      return list[i];
    }
  }
  return { name: "Unknown", location: "-" };
}

// Decide stock status using quantity and minimum stock
function getStockStatus(qty, minStock) {
  if (qty === 0) {
    return "Out of stock";
  } else if (qty < minStock) {
    return "Low stock";
  }
  return "Normal";
}

// Return the CSS badge class for a status text
function getBadgeClass(status) {
  if (status === "Normal" || status === "Active") {
    return "badge-normal";
  } else if (status === "Low stock") {
    return "badge-low";
  } else if (status === "Out of stock" || status === "Inactive") {
    return "badge-out";
  }
  return "badge-info";
}

// Resolved alerts are remembered in the browser (they are not stored in the database)
function loadData(key, defaultValue) {
  var saved = localStorage.getItem(key);
  return saved ? JSON.parse(saved) : defaultValue;
}

function saveData(key, value) {
  localStorage.setItem(key, JSON.stringify(value));
}
