// =========================================================
// history.js - detection history with filter and search
// =========================================================

var events = [];

function showHistory() {
  var searchText = document.getElementById("searchInput").value.toLowerCase();
  var type = document.getElementById("typeFilter").value;
  var body = document.getElementById("historyBody");
  var html = "";
  var count = 0;

  for (var i = 0; i < events.length; i++) {
    var ev = events[i];
    var product = findProduct(ev.productId);
    var shelf = findShelf(ev.shelfId);

    var text = (product.name + " " + shelf.name).toLowerCase();
    if (text.indexOf(searchText) === -1) {
      continue;
    }
    if (type !== "All" && ev.type !== type) {
      continue;
    }

    var badge = "badge-info";
    if (ev.type === "Low stock") {
      badge = "badge-low";
    }

    count++;
    html += "<tr>";
    html += "<td>#" + ev.id + "</td>";
    html += "<td>" + product.name + "</td>";
    html += "<td>" + shelf.name + "</td>";
    html += '<td><span class="badge-status ' + badge + '">' + ev.type + "</span></td>";
    html += "<td>" + ev.qty + "</td>";
    html += "<td>" + ev.time + "</td>";
    html += "</tr>";
  }

  if (count === 0) {
    html = '<tr><td colspan="6" class="text-center text-muted py-4">No events found</td></tr>';
  }

  body.innerHTML = html;
  document.getElementById("eventCount").textContent = count + " event(s)";
}

document.getElementById("searchInput").addEventListener("input", showHistory);
document.getElementById("typeFilter").addEventListener("change", showHistory);

function refresh() {
  loadAll(function () {
    events = getEvents();
    showHistory();
  });
}

refresh();

// new event from the backend -> reload the table
connectSocket(function (message) {
  if (message.type === "stock_event") {
    refresh();
  }
});
