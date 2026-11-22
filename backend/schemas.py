# schemas.py - the shape of data that comes in and goes out of the API
# (Pydantic checks the data for us)

from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field, ConfigDict, field_validator

from .validation import clean_name, clean_email, check_password_rules


# ---------- Login ----------
class LoginIn(BaseModel):
    email: str
    password: str


# ---------- Register ----------
# There is NO role field here. Everyone who registers becomes "Staff".
# An Admin can only be created with:  python -m backend.create_admin
class RegisterIn(BaseModel):
    name: str
    email: str
    password: str

    @field_validator("name")
    @classmethod
    def check_name(cls, value):
        return clean_name(value)

    @field_validator("email")
    @classmethod
    def check_email(cls, value):
        return clean_email(value)

    @field_validator("password")
    @classmethod
    def check_password(cls, value):
        return check_password_rules(value)


class UserOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    user_id: int
    name: str
    email: str
    role: str


class TokenOut(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: UserOut


# ---------- Products ----------
class ProductIn(BaseModel):
    product_name: str = Field(min_length=1, max_length=100)
    category: Optional[str] = "Other"
    minimum_stock: int = Field(default=5, ge=0)
    detect_class: Optional[str] = ""


class ProductOut(ProductIn):
    model_config = ConfigDict(from_attributes=True)
    product_id: int
    created_at: Optional[datetime] = None


# ---------- Shelves ----------
class ShelfIn(BaseModel):
    shelf_name: str = Field(min_length=1, max_length=50)
    location: Optional[str] = ""
    status: str = "Active"
    occupancy: int = Field(default=0, ge=0, le=100)
    roi_x: float = Field(default=0, ge=0, le=100)
    roi_y: float = Field(default=0, ge=0, le=100)
    roi_w: float = Field(default=0, ge=0, le=100)
    roi_h: float = Field(default=0, ge=0, le=100)


class ShelfOut(ShelfIn):
    model_config = ConfigDict(from_attributes=True)
    shelf_id: int


# ---------- Inventory ----------
class InventoryIn(BaseModel):
    product_id: int
    shelf_id: int
    detected_quantity: int = Field(ge=0)


class InventoryOut(InventoryIn):
    model_config = ConfigDict(from_attributes=True)
    inventory_id: int
    updated_at: Optional[datetime] = None


# ---------- Events ----------
class EventOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    event_id: int
    product_id: int
    shelf_id: int
    event_type: str
    quantity: int
    event_time: Optional[datetime] = None


# ---------- Detection ----------
class StartIn(BaseModel):
    source: str = "0"       # "0" = webcam, or a video file name from the videos folder
