# seed.py - put sample data in an empty database
# (runs automatically when the server starts and the tables are empty)

from datetime import datetime, timedelta

from .models import Product, Shelf, Inventory, DetectionEvent


def seed_database(db):
    # NOTE: no users are created here on purpose.
    #   Staff   -> register on the website
    #   Admin   -> python -m backend.create_admin

    # Only add sample products/shelves if the database is empty
    if db.query(Product).count() > 0:
        return

    # ---------- Products ----------
    products = [
        Product(product_name="Cardboard Boxes", category="Packaging", minimum_stock=15, detect_class="box"),
        Product(product_name="Water Bottles", category="Beverages", minimum_stock=10, detect_class="bottle"),
        Product(product_name="Snack Packets", category="Food", minimum_stock=8, detect_class="packet"),
        Product(product_name="Soft Drink Cans", category="Beverages", minimum_stock=12, detect_class="can"),
        Product(product_name="Detergent Bottles", category="Household", minimum_stock=6, detect_class="detergent_bottle"),
        Product(product_name="Cereal Boxes", category="Food", minimum_stock=10, detect_class="cereal_box"),
    ]
    db.add_all(products)

    # ---------- Shelves (ROI values are percent of the camera frame) ----------
    shelves = [
        Shelf(shelf_name="Shelf A", location="Zone 1 - Aisle 1", occupancy=88, roi_x=2, roi_y=5, roi_w=30, roi_h=40),
        Shelf(shelf_name="Shelf B", location="Zone 1 - Aisle 2", occupancy=62, roi_x=35, roi_y=5, roi_w=30, roi_h=40),
        Shelf(shelf_name="Shelf C", location="Zone 2 - Aisle 1", occupancy=24, roi_x=68, roi_y=5, roi_w=30, roi_h=40),
        Shelf(shelf_name="Shelf D", location="Zone 2 - Aisle 2", occupancy=71, roi_x=2, roi_y=52, roi_w=30, roi_h=40),
        Shelf(shelf_name="Shelf E", location="Zone 3 - Aisle 1", occupancy=15, roi_x=35, roi_y=52, roi_w=30, roi_h=40),
        Shelf(shelf_name="Shelf F", location="Zone 3 - Aisle 2", status="Inactive", occupancy=0),
    ]
    db.add_all(shelves)
    db.commit()

    # ---------- Inventory (product index, shelf index, quantity) ----------
    now = datetime.now()
    rows = [(0, 0, 20), (1, 1, 12), (2, 2, 5), (3, 3, 18), (4, 4, 0), (5, 0, 9)]
    for i, (p, s, qty) in enumerate(rows):
        db.add(Inventory(product_id=products[p].product_id, shelf_id=shelves[s].shelf_id,
                         detected_quantity=qty, updated_at=now - timedelta(hours=6 - i)))

    # ---------- A few old events ----------
    events = [
        (2, 2, "Low stock", 5, 5), (4, 4, "Low stock", 0, 4), (5, 0, "Low stock", 9, 3),
        (0, 0, "Stock update", 20, 6), (1, 1, "Stock update", 12, 5), (3, 3, "Stock update", 18, 4),
        (1, 1, "Stock update", 14, 20), (0, 0, "Stock update", 22, 21), (2, 2, "Stock update", 9, 23),
        (3, 3, "Low stock", 11, 26),
    ]
    for p, s, kind, qty, hours_ago in events:
        db.add(DetectionEvent(product_id=products[p].product_id, shelf_id=shelves[s].shelf_id,
                              event_type=kind, quantity=qty, event_time=now - timedelta(hours=hours_ago)))
    db.commit()
