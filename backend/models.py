# models.py - database tables (one class = one table)

from datetime import datetime
from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, UniqueConstraint
from sqlalchemy.orm import relationship

from .database import Base


class User(Base):
    __tablename__ = "users"

    user_id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    email = Column(String(120), unique=True, nullable=False)
    password_hash = Column(String(255), nullable=False)
    role = Column(String(20), default="Staff")          # Admin / Staff


class Product(Base):
    __tablename__ = "products"

    product_id = Column(Integer, primary_key=True, index=True)
    product_name = Column(String(100), nullable=False)
    category = Column(String(50))
    minimum_stock = Column(Integer, default=5)           # alert level
    detect_class = Column(String(50))                    # YOLO class name for this product
    created_at = Column(DateTime, default=datetime.now)

    inventory = relationship("Inventory", back_populates="product", cascade="all, delete-orphan")
    events = relationship("DetectionEvent", back_populates="product", cascade="all, delete-orphan")


class Shelf(Base):
    __tablename__ = "shelves"

    shelf_id = Column(Integer, primary_key=True, index=True)
    shelf_name = Column(String(50), nullable=False)
    location = Column(String(100))
    status = Column(String(20), default="Active")        # Active / Inactive
    occupancy = Column(Integer, default=0)               # filled area in percent (0-100)

    # Shelf region (ROI) as a percent of the camera frame (0-100)
    roi_x = Column(Float, default=0)
    roi_y = Column(Float, default=0)
    roi_w = Column(Float, default=0)
    roi_h = Column(Float, default=0)

    inventory = relationship("Inventory", back_populates="shelf", cascade="all, delete-orphan")
    events = relationship("DetectionEvent", back_populates="shelf", cascade="all, delete-orphan")


class Inventory(Base):
    __tablename__ = "inventory"
    # one row for each product + shelf pair
    __table_args__ = (UniqueConstraint("product_id", "shelf_id", name="uq_product_shelf"),)

    inventory_id = Column(Integer, primary_key=True, index=True)
    product_id = Column(Integer, ForeignKey("products.product_id", ondelete="CASCADE"), nullable=False)
    shelf_id = Column(Integer, ForeignKey("shelves.shelf_id", ondelete="CASCADE"), nullable=False)
    detected_quantity = Column(Integer, default=0)
    updated_at = Column(DateTime, default=datetime.now)

    product = relationship("Product", back_populates="inventory")
    shelf = relationship("Shelf", back_populates="inventory")


class DetectionEvent(Base):
    __tablename__ = "detection_events"

    event_id = Column(Integer, primary_key=True, index=True)
    product_id = Column(Integer, ForeignKey("products.product_id", ondelete="CASCADE"), nullable=False)
    shelf_id = Column(Integer, ForeignKey("shelves.shelf_id", ondelete="CASCADE"), nullable=False)
    event_type = Column(String(30))                      # Stock update / Low stock
    quantity = Column(Integer, default=0)
    event_time = Column(DateTime, default=datetime.now)

    product = relationship("Product", back_populates="events")
    shelf = relationship("Shelf", back_populates="events")
