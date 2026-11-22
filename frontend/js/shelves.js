// =========================================================
// shelves.js - show, add, edit and delete shelves
// A shelf also has a REGION (ROI) = the part of the camera picture
// where this shelf is. Values are percent of the picture (0-100).
// =========================================================

var shelves = [];
var shelfModal = new bootstrap.Modal(document.getElementById("shelfModal"));

// Choose the progress bar colour from occupancy percentage
function getBarClass(percent) {
  if (percent >= 60) {
    return "bar-green";
  } else if (percent >= 30) {
    return "bar-orange";
  }
  return "bar-red";
}

// Text for shelf availability
function getShelfText(shelf) {
  if (shelf.status !== "Active") {
    return "Inactive";
  }
  if (shelf.occupancy >= 60) {
    return "Well stocked";
  } else if (shelf.occupancy >= 30) {
    return "Half full";
  }
  return "Needs restocking";
}

function showShelves() {
  var box = document.getElementById("shelfGrid");
  var html = "";

  for (var i = 0; i < shelves.length; i++) {
    var s = shelves[i];
    var text = getShelfText(s);

    var badge = "badge-normal";
    if (text === "Half full") { badge = "badge-info"; }
    if (text === "Needs restocking") { badge = "badge-low"; }
    if (text === "Inactive") { badge = "badge-out"; }

    var hasRegion = s.roiW > 0 && s.roiH > 0;

    html += '<div class="col-12 col-md-6 col-xl-4">';
    html += '  <div class="shelf-card">';
    html += '    <div class="d-flex justify-content-between align-items-start">';
    html += '      <h5><i class="bi bi-grid-3x3-gap me-2 text-primary"></i>' + s.name + '</h5>';
    html += '      <span class="badge-status ' + badge + '">' + text + '</span>';
    html += '    </div>';
    html += '    <div class="shelf-location"><i class="bi bi-geo-alt"></i> ' + s.location + '</div>';
    html += '    <div class="d-flex justify-content-between mb-1" style="font-size:13px">';
    html += '      <span>Occupied area</span><strong>' + s.occupancy + '%</strong>';
    html += '    </div>';
    html += '    <div class="progress-vs mb-2"><div class="' + getBarClass(s.occupancy) + '" style="width:' + s.occupancy + '%"></div></div>';
    html += '    <div class="text-muted mb-3" style="font-size:12.5px"><i class="bi bi-bounding-box"></i> Camera region: ';
    html += hasRegion ? (s.roiX + "%, " + s.roiY + "% - " + s.roiW + "% x " + s.roiH + "%") : "not set";
    html += '    </div>';
    html += '    <button class="icon-btn" title="Edit" onclick="editShelf(' + s.id + ')"><i class="bi bi-pencil"></i></button>';
    html += '    <button class="icon-btn delete" title="Delete" onclick="deleteShelf(' + s.id + ')"><i class="bi bi-trash"></i></button>';
    html += '  </div>';
    html += '</div>';
  }

  if (shelves.length === 0) {
    html = '<div class="col-12"><p class="text-center text-muted">No shelves yet. Click "Add Shelf".</p></div>';
  }

  box.innerHTML = html;
}

function refresh() {
  loadAll(function () {
    shelves = getShelves();
    showShelves();
  });
}

function openAddShelf() {
  document.getElementById("shelfModalTitle").textContent = "Add New Shelf";
  document.getElementById("shelfForm").reset();
  document.getElementById("shelfId").value = "";
  shelfModal.show();
}

function editShelf(id) {
  for (var i = 0; i < shelves.length; i++) {
    if (shelves[i].id === id) {
      document.getElementById("shelfModalTitle").textContent = "Edit Shelf";
      document.getElementById("shelfId").value = shelves[i].id;
      document.getElementById("shelfName").value = shelves[i].name;
      document.getElementById("shelfLocation").value = shelves[i].location;
      document.getElementById("shelfStatus").value = shelves[i].status;
      document.getElementById("shelfOccupancy").value = shelves[i].occupancy;
      document.getElementById("roiX").value = shelves[i].roiX;
      document.getElementById("roiY").value = shelves[i].roiY;
      document.getElementById("roiW").value = shelves[i].roiW;
      document.getElementById("roiH").value = shelves[i].roiH;
    }
  }
  shelfModal.show();
}

function deleteShelf(id) {
  if (!confirm("Delete this shelf?\nIts inventory records and events will also be deleted.")) {
    return;
  }

  api("DELETE", "/api/shelves/" + id)
    .then(function () {
      showToast("Shelf deleted");
      refresh();
    })
    .catch(function (error) {
      showToast(error.message);
    });
}

document.getElementById("shelfForm").addEventListener("submit", function (e) {
  e.preventDefault();

  var id = document.getElementById("shelfId").value;
  var data = {
    shelf_name: document.getElementById("shelfName").value.trim(),
    location: document.getElementById("shelfLocation").value.trim(),
    status: document.getElementById("shelfStatus").value,
    occupancy: parseInt(document.getElementById("shelfOccupancy").value) || 0,
    roi_x: parseFloat(document.getElementById("roiX").value) || 0,
    roi_y: parseFloat(document.getElementById("roiY").value) || 0,
    roi_w: parseFloat(document.getElementById("roiW").value) || 0,
    roi_h: parseFloat(document.getElementById("roiH").value) || 0
  };

  var request;
  if (id === "") {
    request = api("POST", "/api/shelves", data);
  } else {
    request = api("PUT", "/api/shelves/" + id, data);
  }

  request
    .then(function () {
      showToast(id === "" ? "Shelf added" : "Shelf updated");
      shelfModal.hide();
      refresh();
    })
    .catch(function (error) {
      showToast(error.message);
    });
});

document.getElementById("addShelfBtn").addEventListener("click", openAddShelf);

refresh();
