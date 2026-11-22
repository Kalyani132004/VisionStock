# routes/alerts.py - detection events (history) and low-stock alerts

from typing import List, Optional
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from ..database import get_db
from ..models import DetectionEvent, Inventory, Shelf
from ..schemas import EventOut
from ..security import get_current_user
from ..services.inventory_service import get_status

router = APIRouter(prefix="/api", tags=["Events and Alerts"], dependencies=[Depends(get_current_user)])


@router.get("/events", response_model=List[EventOut])
def get_events(limit: int = 200, event_type: Optional[str] = None, db: Session = Depends(get_db)):
    query = db.query(DetectionEvent)
    if event_type:
        query = query.filter(DetectionEvent.event_type == event_type)
    # newest first
    return query.order_by(DetectionEvent.event_time.desc(), DetectionEvent.event_id.desc()).limit(limit).all()


@router.get("/alerts")
def get_alerts(db: Session = Depends(get_db)):
    alerts = []

    # 1. products below the minimum stock
    for row in db.query(Inventory).all():
        status = get_status(row.detected_quantity, row.product.minimum_stock)
        if status != "Normal":
            alerts.append({
                "type": "product",
                "title": row.product.product_name + " - " + status,
                "message": row.shelf.shelf_name + " has " + str(row.detected_quantity) +
                           " units (minimum " + str(row.product.minimum_stock) + ")",
                "level": "high" if status == "Out of stock" else "medium",
                "time": row.updated_at,
            })

    # 2. active shelves that are almost empty
    for shelf in db.query(Shelf).filter(Shelf.status == "Active").all():
        if shelf.occupancy < 30:
            alerts.append({
                "type": "shelf",
                "title": shelf.shelf_name + " - Needs restocking",
                "message": "Only " + str(shelf.occupancy) + "% of the shelf area is occupied",
                "level": "medium",
                "time": None,
            })

    return alerts
