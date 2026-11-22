// =========================================================
// dashboard.js - summary cards, charts and recent alerts
// =========================================================

var products = [];
var shelves = [];
var inventory = [];
var events = [];
var stockChartObj = null;
var shelfChartObj = null;

// ---------- 1. Summary cards ----------
function showSummary() {
  var totalProducts = 0;
  var lowStockCount = 0;
  var activeShelves = 0;

  for (var i = 0; i < inventory.length; i++) {
    totalProducts = totalProducts + inventory[i].qty;

    var product = findProduct(inventory[i].productId);
    var status = getStockStatus(inventory[i].qty, product.minStock);
    if (status !== "Normal") {
      lowStockCount++;
    }
  }

  for (var j = 0; j < shelves.length; j++) {
    if (shelves[j].status === "Active") {
      activeShelves++;
    }
  }

  document.getElementById("totalProducts").textContent = totalProducts;
  document.getElementById("activeShelves").textContent = activeShelves;
  document.getElementById("lowStock").textContent = lowStockCount;
  document.getElementById("totalEvents").textContent = events.length;
}

// ---------- 2. Bar chart: stock by product ----------
function showStockChart() {
  var names = [];
  var quantities = [];
  var colors = [];

  for (var i = 0; i < inventory.length; i++) {
    var product = findProduct(inventory[i].productId);
    names.push(product.name);
    quantities.push(inventory[i].qty);

    // red / orange / blue depending on status
    var status = getStockStatus(inventory[i].qty, product.minStock);
    if (status === "Out of stock") {
      colors.push("#d64545");
    } else if (status === "Low stock") {
      colors.push("#e8890c");
    } else {
      colors.push("#2f6fed");
    }
  }

  if (stockChartObj) {
    stockChartObj.destroy();      // remove the old chart before drawing a new one
  }
  stockChartObj = new Chart(document.getElementById("stockChart"), {
    type: "bar",
    data: {
      labels: names,
      datasets: [{
        label: "Detected quantity",
        data: quantities,
        backgroundColor: colors,
        borderRadius: 6
      }]
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      plugins: { legend: { display: false } },
      scales: { y: { beginAtZero: true } }
    }
  });
}

// ---------- 3. Doughnut chart: shelf availability ----------
function showShelfChart() {
  var good = 0;   // 60% or more
  var medium = 0; // 30% to 59%
  var low = 0;    // below 30%

  for (var i = 0; i < shelves.length; i++) {
    if (shelves[i].status !== "Active") {
      continue;
    }
    if (shelves[i].occupancy >= 60) {
      good++;
    } else if (shelves[i].occupancy >= 30) {
      medium++;
    } else {
      low++;
    }
  }

  if (shelfChartObj) {
    shelfChartObj.destroy();
  }
  shelfChartObj = new Chart(document.getElementById("shelfChart"), {
    type: "doughnut",
    data: {
      labels: ["Well stocked", "Half full", "Nearly empty"],
      datasets: [{
        data: [good, medium, low],
        backgroundColor: ["#1e9e63", "#e8890c", "#d64545"],
        borderWidth: 2
      }]
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      cutout: "62%",
      plugins: { legend: { position: "bottom" } }
    }
  });
}

// ---------- 4. Recent alerts list ----------
function showRecentAlerts() {
  var box = document.getElementById("recentAlerts");
  var html = "";

  // show only the first 5 events
  for (var i = 0; i < 5 && i < events.length; i++) {
    var ev = events[i];
    var product = findProduct(ev.productId);
    var shelf = findShelf(ev.shelfId);

    var iconClass = "bi-arrow-repeat";
    var colorClass = "icon-blue";
    if (ev.type === "Low stock") {
      iconClass = "bi-exclamation-triangle";
      colorClass = "icon-orange";
    }

    html += '<div class="alert-item">';
    html += '  <div class="alert-dot ' + colorClass + '"><i class="bi ' + iconClass + '"></i></div>';
    html += '  <div class="alert-text">';
    html += '    <strong>' + shelf.name + ' - ' + ev.type + '</strong>';
    html += '    <span>' + product.name + ': ' + ev.qty + ' units &bull; ' + ev.time + '</span>';
    html += '  </div>';
    html += '</div>';
  }

  box.innerHTML = html;
}

// ---------- 5. Low stock table ----------
function showLowStockTable() {
  var body = document.getElementById("lowStockBody");
  var html = "";

  for (var i = 0; i < inventory.length; i++) {
    var item = inventory[i];
    var product = findProduct(item.productId);
    var status = getStockStatus(item.qty, product.minStock);

    if (status !== "Normal") {
      html += "<tr>";
      html += "<td>" + product.name + "</td>";
      html += "<td>" + findShelf(item.shelfId).name + "</td>";
      html += "<td>" + item.qty + " / " + product.minStock + "</td>";
      html += '<td><span class="badge-status ' + getBadgeClass(status) + '">' + status + "</span></td>";
      html += "</tr>";
    }
  }

  if (html === "") {
    html = '<tr><td colspan="4" class="text-center text-muted">No low stock products</td></tr>';
  }
  body.innerHTML = html;
}

// Load data from the backend, then show everything
function refresh() {
  loadAll(function () {
    products = getProducts();
    shelves = getShelves();
    inventory = getInventory();
    events = getEvents();

    showSummary();
    showStockChart();
    showShelfChart();
    showRecentAlerts();
    showLowStockTable();
  });
}

refresh();

// Live updates: the backend sends a message through WebSocket
// when stock changes. We show a message and reload the numbers.
connectSocket(function (message) {
  if (message.type === "stock_event") {
    showToast(message.shelf + ": " + message.product + " - " + message.event_type + " (" + message.quantity + ")");
  }
  refresh();
});
