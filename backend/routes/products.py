# routes/products.py - products CRUD

from typing import List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from ..database import get_db
from ..models import Product
from ..schemas import ProductIn, ProductOut
from ..security import get_current_user, admin_only

router = APIRouter(prefix="/api/products", tags=["Products"], dependencies=[Depends(get_current_user)])


def find_product(db, product_id):
    product = db.query(Product).filter(Product.product_id == product_id).first()
    if product is None:
        raise HTTPException(status_code=404, detail="Product not found")
    return product


@router.get("", response_model=List[ProductOut])
def get_products(db: Session = Depends(get_db)):
    return db.query(Product).order_by(Product.product_id).all()


@router.post("", response_model=ProductOut, status_code=201)
def add_product(data: ProductIn, db: Session = Depends(get_db)):
    product = Product(
        product_name=data.product_name.strip(),
        category=data.category,
        minimum_stock=data.minimum_stock,
        detect_class=(data.detect_class or "").strip().lower(),
    )
    db.add(product)
    db.commit()
    db.refresh(product)
    return product


@router.put("/{product_id}", response_model=ProductOut)
def update_product(product_id: int, data: ProductIn, db: Session = Depends(get_db)):
    product = find_product(db, product_id)
    product.product_name = data.product_name.strip()
    product.category = data.category
    product.minimum_stock = data.minimum_stock
    product.detect_class = (data.detect_class or "").strip().lower()
    db.commit()
    db.refresh(product)
    return product


# Only Admin can delete
@router.delete("/{product_id}", dependencies=[Depends(admin_only)])
def delete_product(product_id: int, db: Session = Depends(get_db)):
    product = find_product(db, product_id)
    db.delete(product)
    db.commit()
    return {"message": "Product deleted"}
