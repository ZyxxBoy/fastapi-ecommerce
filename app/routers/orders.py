from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import select

from .. import models, schemas
from ..deps import get_db, get_current_user

router = APIRouter(prefix="/orders", tags=["orders"])


@router.post("/", response_model=schemas.OrderOut, status_code=status.HTTP_201_CREATED)
def create_order(
    order_in: schemas.OrderCreate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    if not order_in.items:
        raise HTTPException(status_code=400, detail="Order must contain at least one item")

    try:
        total_price = 0.0

        # buat order dulu (status PENDING)
        order = models.Order(user_id=current_user.id, total_price=0.0, status="PENDING")
        db.add(order)
        db.flush()  # supaya order.id terisi

        for item in order_in.items:
            # kunci baris product (row-level lock) supaya stok aman
            product = (
                db.execute(
                    select(models.Product)
                    .where(models.Product.id == item.product_id)
                    .with_for_update()
                ).scalar_one_or_none()
            )
            if not product or not product.is_active:
                raise HTTPException(
                    status_code=400,
                    detail=f"Product {item.product_id} not available",
                )

            if product.stock < item.quantity:
                raise HTTPException(
                    status_code=400,
                    detail=f"Insufficient stock for {product.name}",
                )

            # update stok
            product.stock -= item.quantity
            line_price = product.price * item.quantity
            total_price += line_price

            # buat OrderItem
            order_item = models.OrderItem(
                order_id=order.id,
                product_id=product.id,
                quantity=item.quantity,
                unit_price=product.price,
            )
            db.add(order_item)

        # update total & status
        order.total_price = total_price
        order.status = "CONFIRMED"

        db.commit()
        db.refresh(order)
        return order

    except:
        db.rollback()
        raise
