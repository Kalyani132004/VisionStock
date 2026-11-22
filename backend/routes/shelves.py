# routes/shelves.py - shelves CRUD

from typing import List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from ..database import get_db
from ..models import Shelf
from ..schemas import ShelfIn, ShelfOut
from ..security import get_current_user, admin_only

router = APIRouter(prefix="/api/shelves", tags=["Shelves"], dependencies=[Depends(get_current_user)])


def find_shelf(db, shelf_id):
    shelf = db.query(Shelf).filter(Shelf.shelf_id == shelf_id).first()
    if shelf is None:
        raise HTTPException(status_code=404, detail="Shelf not found")
    return shelf


def check_roi(data: ShelfIn):
    # the region must stay inside the camera frame
    if data.roi_x + data.roi_w > 100 or data.roi_y + data.roi_h > 100:
        raise HTTPException(status_code=422, detail="Shelf region goes outside the frame (x + width and y + height must be 100 or less)")


@router.get("", response_model=List[ShelfOut])
def get_shelves(db: Session = Depends(get_db)):
    return db.query(Shelf).order_by(Shelf.shelf_id).all()


@router.post("", response_model=ShelfOut, status_code=201)
def add_shelf(data: ShelfIn, db: Session = Depends(get_db)):
    check_roi(data)
    shelf = Shelf(**data.model_dump())
    db.add(shelf)
    db.commit()
    db.refresh(shelf)
    return shelf


@router.put("/{shelf_id}", response_model=ShelfOut)
def update_shelf(shelf_id: int, data: ShelfIn, db: Session = Depends(get_db)):
    check_roi(data)
    shelf = find_shelf(db, shelf_id)
    for field, value in data.model_dump().items():
        setattr(shelf, field, value)
    db.commit()
    db.refresh(shelf)
    return shelf


@router.delete("/{shelf_id}", dependencies=[Depends(admin_only)])
def delete_shelf(shelf_id: int, db: Session = Depends(get_db)):
    shelf = find_shelf(db, shelf_id)
    db.delete(shelf)
    db.commit()
    return {"message": "Shelf deleted"}
