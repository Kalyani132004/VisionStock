# inventory_service.py - the inventory logic
# Both the camera pipeline and the manual API use these functions.

from datetime import datetime

from ..config import KAFKA_ENABLED
from ..models import Inventory, DetectionEvent
from . import kafka_service
from .websocket_service import manager


def get_status(qty, minimum):
    """Normal / Low stock / Out of stock"""
    if qty == 0:
        return "Out of stock"
    if qty < minimum:
        return "Low stock"
    return "Normal"


def send_notification(message: dict):
    """With Kafka: publish the event (the consumer sends it to the browser).
    Without Kafka: send it to the browser directly with WebSocket."""
    if KAFKA_ENABLED:
        if kafka_service.publish_event(message):
            return
    manager.broadcast_from_thread(message)


def update_stock(db, product, shelf, qty):
    """Save a new quantity for a product on a shelf.
    Creates 'Stock update' and 'Low stock' events when needed.
    Returns True if something changed."""
    now = datetime.now()
    row = db.query(Inventory).filter(
        Inventory.product_id == product.product_id,
        Inventory.shelf_id == shelf.shelf_id,
    ).first()

    old_qty = None
    if row is None:
        row = Inventory(product_id=product.product_id, shelf_id=shelf.shelf_id,
                        detected_quantity=qty, updated_at=now)
        db.add(row)
    else:
        old_qty = row.detected_quantity
        if old_qty == qty:
            return False              # nothing changed
        row.detected_quantity = qty
        row.updated_at = now

    # list of (event type) to store
    event_types = ["Stock update"]

    new_status = get_status(qty, product.minimum_stock)
    if old_qty is None:
        old_status = "Normal"
    else:
        old_status = get_status(old_qty, product.minimum_stock)

    # alert only when the status gets worse (avoids too many alerts)
    if new_status != "Normal" and new_status != old_status:
        event_types.append("Low stock")

    for kind in event_types:
        db.add(DetectionEvent(product_id=product.product_id, shelf_id=shelf.shelf_id,
                              event_type=kind, quantity=qty, event_time=now))
    db.commit()

    # tell the dashboard
    for kind in event_types:
        send_notification({
            "type": "stock_event",
            "event_type": kind,
            "product": product.product_name,
            "shelf": shelf.shelf_name,
            "quantity": qty,
            "status": new_status,
            "time": now.strftime("%Y-%m-%d %H:%M"),
        })
    return True


def update_shelf_occupancy(db, shelf, percent):
    """Save how much of the shelf area is filled."""
    percent = int(max(0, min(100, percent)))
    if shelf.occupancy == percent:
        return
    shelf.occupancy = percent
    db.commit()
    send_notification({
        "type": "shelf_update",
        "shelf": shelf.shelf_name,
        "occupancy": percent,
    })
