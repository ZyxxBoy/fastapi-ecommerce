from fastapi import FastAPI
from .database import Base, engine
from .routers import auth, products, orders

Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Mini E-Commerce API",
    version="0.1.0"
)

app.include_router(auth.router)
app.include_router(products.router)
app.include_router(orders.router)
