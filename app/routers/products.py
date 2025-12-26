from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from redis import Redis
from typing import List

from .. import models, schemas
from ..deps import get_db, get_redis

router = APIRouter(prefix="/products", tags=["products"])

POPULAR_KEY = "popular_products"

@router.post("/", response_model=schemas.ProductOut)
def create_product(product_in: schemas.ProductCreate, db: Session = Depends(get_db)):
    product = models.Product(**product_in.dict())
    db.add(product)
    db.commit()
    db.refresh(product)
    return product

@router.get("/", response_model=List[schemas.ProductOut])
def list_products(db: Session = Depends(get_db)):
    return db.query(models.Product).filter(models.Product.is_active == True).all()

@router.get("/popular", response_model=List[schemas.ProductOut])
def get_popular_products(db: Session = Depends(get_db), redis: Redis = Depends(get_redis)):
    cached_ids = redis.lrange(POPULAR_KEY, 0, -1)
    if cached_ids:
        return db.query(models.Product).filter(models.Product.id.in_(cached_ids)).all()

    products = db.query(models.Product).limit(5).all()
    if products:
        redis.delete(POPULAR_KEY)
        for p in products:
            redis.rpush(POPULAR_KEY, p.id)
    return products
