from fastapi import FastAPI
from api.api1 import router as products_router
from api.api2 import router as orders_router
from api.auth import router as aut_router

app = FastAPI()

app.include_router(products_router)
app.include_router(orders_router)
app.include_router(aut_router)


@app.get("/")
async def root():
    return {"message": "Bienvenido a la API de gestión de productos y pedidos"}
