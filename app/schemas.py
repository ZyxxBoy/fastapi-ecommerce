from pydantic import BaseModel, EmailStr
from typing import List, Optional
from datetime import datetime

# ===== User & Auth =====
class UserCreate(BaseModel):
    email: EmailStr
    password: str

class UserOut(BaseModel):
    id: int
    email: EmailStr

    class Config:
        orm_mode = True

class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"

# ===== Products =====
class ProductBase(BaseModel):
    name: str
    description: Optional[str] = None
    price: float
    stock: int

class ProductCreate(ProductBase):
    pass

class ProductOut(ProductBase):
    id: int
    is_active: bool

    class Config:
        orm_mode = True

# ===== Orders =====
class OrderItemIn(BaseModel):
    product_id: int
    quantity: int

class OrderCreate(BaseModel):
    items: List[OrderItemIn]

class OrderItemOut(BaseModel):
    product_id: int
    quantity: int
    unit_price: float

    class Config:
        orm_mode = True

class OrderOut(BaseModel):
    id: int
    total_price: float
    status: str
    created_at: datetime
    items: List[OrderItemOut]

    class Config:
        orm_mode = True
