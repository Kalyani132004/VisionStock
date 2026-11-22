// =========================================================
// alerts.js - low stock alerts (mark as resolved)
// =========================================================

var inventory = [];
var shelves = [];

// ids of alerts that user already resolved
var resolved = loadData("vs_resolved", []);

function isResolved(key) {
  return resolved.indexOf(key) !== -1;
}

// Build the alert list from the inventory + shelves
function buildAlerts() {
  var list = [];

  // 1. product alerts
  for (var i = 0; i < inventory.length; i++) {
    var item = inventory[i];
    var product = findProduct(item.productId);
    var status = getStockStatus(item.qty, product.minStock);

    if (status !== "Normal") {
      list.push({
        key: "inv" + item.id,
        title: product.name + " - " + status,
        text: findShelf(item.shelfId).name + " has " + item.qty + " units (minimum " + product.minStock + ")",
        level: status === "Out of stock" ? "high" : "medium",
        time: item.updated
      });
    }
  }

  // 2. shelf alerts (low occupied area)
  for (var j = 0; j < shelves.length; j++) {
    var shelf = shelves[j];
    if (shelf.status === "Active" && shelf.occupancy < 30) {
      list.push({
        key: "shelf" + shelf.id,
        title: shelf.name + " - Needs restocking",
        text: "Only " + shelf.occupancy + "% of the shelf area is occupied",
        level: "medium",
        time: "Latest scan"
      });
    }
  }
  return list;
}

function showAlerts() {
  var alerts = buildAlerts();
  var box = document.getElementById("alertList");
  var html = "";
  var openCount = 0;

  for (var i = 0; i < alerts.length; i++) {
    var a = alerts[i];
    var done = isResolved(a.key);
    if (!done) { openCount++; }

    var colorClass = a.level === "high" ? "icon-orange" : "icon-blue";
    var icon = a.level === "high" ? "bi-x-octagon" : "bi-exclamation-triangle";
    if (a.level === "high") { colorClass = "badge-out"; }
    if (a.level === "medium") { colorClass = "badge-low"; }

    html += '<div class="alert-item ' + (done ? "alert-resolved" : "") + '">';
    html += '  <div class="alert-dot ' + colorClass + '"><i class="bi ' + icon + '"></i></div>';
    html += '  <div class="alert-text"><strong>' + a.title + '</strong><span>' + a.text + ' &bull; ' + a.time + '</span></div>';
    if (done) {
      html += '  <span class="badge-status badge-normal">Resolved</span>';
    } else {
      html += '  <button class="btn-outline-navy btn-sm" onclick="resolveAlert(\'' + a.key + '\')">Mark resolved</button>';
    }
    html += '</div>';
  }

  if (html === "") {
    html = '<p class="text-center text-muted my-4">No alerts. All shelves are fine.</p>';
  }

  box.innerHTML = html;
  document.getElementById("openCount").textContent = openCount;
  document.getElementById("totalCount").textContent = alerts.length;
}

function resolveAlert(key) {
  resolved.push(key);
  saveData("vs_resolved", resolved);
  showAlerts();
  showToast("Alert marked as resolved");
}

function resetAlerts() {
  resolved = [];
  saveData("vs_resolved", resolved);
  showAlerts();
}

document.getElementById("resetBtn").addEventListener("click", resetAlerts);

function refresh() {
  loadAll(function () {
    inventory = getInventory();
    shelves = getShelves();
    showAlerts();
  });
}

refresh();

// live update: new alert from the backend
connectSocket(function (message) {
  if (message.type === "stock_event" && message.event_type === "Low stock") {
    showToast("New alert: " + message.product + " is low on " + message.shelf);
  }
  refresh();
});
