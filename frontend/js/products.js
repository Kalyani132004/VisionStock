// =========================================================
// products.js - add, edit, delete and search products
// All changes are saved in the database through the API.
// =========================================================

var products = [];
var productModal = new bootstrap.Modal(document.getElementById("productModal"));

// ---------- Show products in the table ----------
function showProducts() {
  var searchText = document.getElementById("searchInput").value;
  var body = document.getElementById("productBody");
  var html = "";
  var count = 0;

  for (var i = 0; i < products.length; i++) {
    var p = products[i];

    // search by name or category
    if (searchText) {
      var text = (p.name + " " + p.category).toLowerCase();
      if (text.indexOf(searchText.toLowerCase()) === -1) {
        continue;
      }
    }

    count++;
    html += "<tr>";
    html += "<td>" + p.id + "</td>";
    html += "<td><strong>" + p.name + "</strong></td>";
    html += "<td>" + p.category + "</td>";
    html += "<td>" + (p.detectClass ? "<code>" + p.detectClass + "</code>" : "-") + "</td>";
    html += "<td>" + p.minStock + "</td>";
    html += "<td>";
    html += '<button class="icon-btn" title="Edit" onclick="editProduct(' + p.id + ')"><i class="bi bi-pencil"></i></button>';
    html += '<button class="icon-btn delete" title="Delete" onclick="deleteProduct(' + p.id + ')"><i class="bi bi-trash"></i></button>';
    html += "</td>";
    html += "</tr>";
  }

  if (count === 0) {
    html = '<tr><td colspan="6" class="text-center text-muted py-4">No products found</td></tr>';
  }

  body.innerHTML = html;
  document.getElementById("productCount").textContent = count + " product(s)";
}

// ---------- Reload from the backend, then show ----------
function refresh() {
  loadAll(function () {
    products = getProducts();
    showProducts();
  });
}

// ---------- Open modal to add a product ----------
function openAddModal() {
  document.getElementById("modalTitle").textContent = "Add New Product";
  document.getElementById("productId").value = "";
  document.getElementById("productForm").reset();
  productModal.show();
}

// ---------- Open modal to edit a product ----------
function editProduct(id) {
  for (var i = 0; i < products.length; i++) {
    if (products[i].id === id) {
      document.getElementById("modalTitle").textContent = "Edit Product";
      document.getElementById("productId").value = products[i].id;
      document.getElementById("productName").value = products[i].name;
      document.getElementById("productCategory").value = products[i].category;
      document.getElementById("productClass").value = products[i].detectClass;
      document.getElementById("productMin").value = products[i].minStock;
    }
  }
  productModal.show();
}

// ---------- Delete a product (Admin only) ----------
function deleteProduct(id) {
  if (!confirm("Are you sure you want to delete this product?\nIts inventory records and events will also be deleted.")) {
    return;
  }

  api("DELETE", "/api/products/" + id)
    .then(function () {
      showToast("Product deleted");
      refresh();
    })
    .catch(function (error) {
      showToast(error.message);
    });
}

// ---------- Save form (add or edit) ----------
document.getElementById("productForm").addEventListener("submit", function (e) {
  e.preventDefault();

  var id = document.getElementById("productId").value;
  var data = {
    product_name: document.getElementById("productName").value.trim(),
    category: document.getElementById("productCategory").value,
    detect_class: document.getElementById("productClass").value.trim(),
    minimum_stock: parseInt(document.getElementById("productMin").value)
  };

  var request;
  if (id === "") {
    request = api("POST", "/api/products", data);
  } else {
    request = api("PUT", "/api/products/" + id, data);
  }

  request
    .then(function () {
      showToast(id === "" ? "Product added" : "Product updated");
      productModal.hide();
      refresh();
    })
    .catch(function (error) {
      showToast(error.message);
    });
});

document.getElementById("searchInput").addEventListener("input", showProducts);
document.getElementById("addBtn").addEventListener("click", openAddModal);

refresh();
