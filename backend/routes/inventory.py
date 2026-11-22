# routes/inventory.py - inventory list and manual changes

from typing import List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from ..database import get_db
from ..models import Inventory, Product, Shelf
from ..schemas import InventoryIn, InventoryOut
from ..security import get_current_user, admin_only
from ..services import inventory_service

router = APIRouter(prefix="/api/inventory", tags=["Inventory"], dependencies=[Depends(get_current_user)])


@router.get("", response_model=List[InventoryOut])
def get_inventory(db: Session = Depends(get_db)):
    return db.query(Inventory).order_by(Inventory.inventory_id).all()


# Add a record, or change the quantity if that product is already on that shelf.
# (Useful for manual correction when the camera cannot see something.)
@router.post("", response_model=InventoryOut)
def save_inventory(data: InventoryIn, db: Session = Depends(get_db)):
    product = db.query(Product).filter(Product.product_id == data.product_id).first()
    shelf = db.query(Shelf).filter(Shelf.shelf_id == data.shelf_id).first()
    if product is None or shelf is None:
        raise HTTPException(status_code=404, detail="Product or shelf not found")

    inventory_service.update_stock(db, product, shelf, data.detected_quantity)

    return db.query(Inventory).filter(
        Inventory.product_id == data.product_id,
        Inventory.shelf_id == data.shelf_id,
    ).first()


@router.put("/{inventory_id}", response_model=InventoryOut)
def change_quantity(inventory_id: int, data: InventoryIn, db: Session = Depends(get_db)):
    row = db.query(Inventory).filter(Inventory.inventory_id == inventory_id).first()
    if row is None:
        raise HTTPException(status_code=404, detail="Inventory record not found")

    inventory_service.update_stock(db, row.product, row.shelf, data.detected_quantity)
    db.refresh(row)
    return row


@router.delete("/{inventory_id}", dependencies=[Depends(admin_only)])
def delete_inventory(inventory_id: int, db: Session = Depends(get_db)):
    row = db.query(Inventory).filter(Inventory.inventory_id == inventory_id).first()
    if row is None:
        raise HTTPException(status_code=404, detail="Inventory record not found")
    db.delete(row)
    db.commit()
    return {"message": "Inventory record deleted"}
