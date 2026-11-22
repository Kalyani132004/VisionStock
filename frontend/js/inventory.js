// =========================================================
// inventory.js - inventory table with search, filter, CSV export
// The camera updates the quantities automatically. Here a person can
// also correct a quantity by hand (for example when the camera cannot
// see a product).
// =========================================================

var inventory = [];
var inventoryModal = new bootstrap.Modal(document.getElementById("inventoryModal"));

function showInventory() {
  var searchText = document.getElementById("searchInput").value.toLowerCase();
  var filter = document.getElementById("statusFilter").value;
  var body = document.getElementById("inventoryBody");
  var html = "";
  var count = 0;

  for (var i = 0; i < inventory.length; i++) {
    var item = inventory[i];
    var product = findProduct(item.productId);
    var shelf = findShelf(item.shelfId);
    var status = getStockStatus(item.qty, product.minStock);

    // apply search
    var text = (product.name + " " + shelf.name).toLowerCase();
    if (text.indexOf(searchText) === -1) {
      continue;
    }
    // apply status filter
    if (filter !== "All" && status !== filter) {
      continue;
    }

    // stock level bar (quantity compared with 2 x minimum stock)
    var percent = Math.round((item.qty / (product.minStock * 2)) * 100);
    if (percent > 100) { percent = 100; }
    var barClass = "bar-green";
    if (status === "Low stock") { barClass = "bar-orange"; }
    if (status === "Out of stock") { barClass = "bar-red"; }

    count++;
    html += "<tr>";
    html += "<td><strong>" + product.name + "</strong><br><small class='text-muted'>" + product.category + "</small></td>";
    html += "<td>" + shelf.name + "</td>";
    html += "<td>" + item.qty + "</td>";
    html += "<td>" + product.minStock + "</td>";
    html += '<td style="min-width:120px"><div class="progress-vs"><div class="' + barClass + '" style="width:' + percent + '%"></div></div></td>';
    html += '<td><span class="badge-status ' + getBadgeClass(status) + '">' + status + "</span></td>";
    html += "<td>" + item.updated + "</td>";
    html += "<td>";
    html += '<button class="icon-btn" title="Change quantity" onclick="changeQuantity(' + item.id + ')"><i class="bi bi-pencil"></i></button>';
    html += '<button class="icon-btn delete" title="Delete" onclick="deleteRecord(' + item.id + ')"><i class="bi bi-trash"></i></button>';
    html += "</td>";
    html += "</tr>";
  }

  if (count === 0) {
    html = '<tr><td colspan="8" class="text-center text-muted py-4">No inventory records found</td></tr>';
  }

  body.innerHTML = html;
  document.getElementById("recordCount").textContent = count + " record(s)";
}

function refresh() {
  loadAll(function () {
    inventory = getInventory();
    showInventory();
  });
}

// ---------- Change the quantity of one record ----------
function changeQuantity(id) {
  var item = null;
  for (var i = 0; i < inventory.length; i++) {
    if (inventory[i].id === id) {
      item = inventory[i];
    }
  }
  if (item === null) {
    return;
  }

  var answer = prompt("New quantity for " + findProduct(item.productId).name + " on " + findShelf(item.shelfId).name + ":", item.qty);
  if (answer === null) {
    return;                      // user pressed Cancel
  }

  var qty = parseInt(answer);
  if (isNaN(qty) || qty < 0) {
    showToast("Please enter a number (0 or more)");
    return;
  }

  api("PUT", "/api/inventory/" + id, {
    product_id: item.productId,
    shelf_id: item.shelfId,
    detected_quantity: qty
  }).then(function () {
    showToast("Quantity updated");
    refresh();
  }).catch(function (error) {
    showToast(error.message);
  });
}

// ---------- Delete a record (Admin only) ----------
function deleteRecord(id) {
  if (!confirm("Delete this inventory record?")) {
    return;
  }
  api("DELETE", "/api/inventory/" + id)
    .then(function () {
      showToast("Record deleted");
      refresh();
    })
    .catch(function (error) {
      showToast(error.message);
    });
}

// ---------- Add record modal ----------
function openAddRecord() {
  var products = getProducts();
  var shelves = getShelves();

  var productHtml = "";
  for (var i = 0; i < products.length; i++) {
    productHtml += '<option value="' + products[i].id + '">' + products[i].name + "</option>";
  }
  var shelfHtml = "";
  for (var j = 0; j < shelves.length; j++) {
    shelfHtml += '<option value="' + shelves[j].id + '">' + shelves[j].name + "</option>";
  }

  document.getElementById("recordProduct").innerHTML = productHtml;
  document.getElementById("recordShelf").innerHTML = shelfHtml;
  document.getElementById("recordQty").value = "";
  inventoryModal.show();
}

document.getElementById("inventoryForm").addEventListener("submit", function (e) {
  e.preventDefault();

  api("POST", "/api/inventory", {
    product_id: parseInt(document.getElementById("recordProduct").value),
    shelf_id: parseInt(document.getElementById("recordShelf").value),
    detected_quantity: parseInt(document.getElementById("recordQty").value)
  }).then(function () {
    showToast("Record saved");
    inventoryModal.hide();
    refresh();
  }).catch(function (error) {
    showToast(error.message);
  });
});

// ---------- Download table as a CSV file ----------
function exportCSV() {
  var csv = "Product,Shelf,Quantity,Minimum Stock,Status,Last Updated\n";

  for (var i = 0; i < inventory.length; i++) {
    var item = inventory[i];
    var product = findProduct(item.productId);
    var shelf = findShelf(item.shelfId);
    var status = getStockStatus(item.qty, product.minStock);

    csv += product.name + "," + shelf.name + "," + item.qty + "," + product.minStock + "," + status + "," + item.updated + "\n";
  }

  var blob = new Blob([csv], { type: "text/csv" });
  var link = document.createElement("a");
  link.href = URL.createObjectURL(blob);
  link.download = "inventory_report.csv";
  link.click();
  showToast("Report downloaded");
}

document.getElementById("searchInput").addEventListener("input", showInventory);
document.getElementById("statusFilter").addEventListener("change", showInventory);
document.getElementById("exportBtn").addEventListener("click", exportCSV);
document.getElementById("addRecordBtn").addEventListener("click", openAddRecord);

refresh();

// live update: when the backend sends a stock event, reload the table
connectSocket(function (message) {
  if (message.type === "stock_event") {
    refresh();
  }
});
