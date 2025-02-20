from fastapi import HTTPException, Depends, status, APIRouter
from pydantic import BaseModel
from datetime import datetime
from typing import List
from .auth import get_db_connection, get_current_user


# Router URL for authentication for "pedidos"
router = APIRouter(prefix="/internal/api/v1/pedidos", tags=["pedidos"])


# Pydantic models for data validation
class OrderItem(BaseModel):
    product_id: int
    quantity: int 

class OrderCreate(BaseModel):
    items: List[OrderItem]

class OrderResponse(BaseModel):
    order_id: int
    order_date: datetime
    items: List[dict]
    total_price: float


# Endpoint to create an order with validation and secured by user authentication by JWT
@router.post("/", status_code=status.HTTP_201_CREATED)
async def order_create(order: OrderCreate, current_user: dict = Depends(get_current_user)):
    if current_user["user_role"] != "admin":
        raise HTTPException(
            status_code = status.HTTP_403_FORBIDDEN,
            detail = "No tienes permisos para realizar esta accion"
        )

    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        for item in order.items:
            if item.quantity < 1:
                raise HTTPException(
                    status_code = status.HTTP_400_BAD_REQUEST,
                    detail = f"El stock del producto [{item.product_id}] debe ser mayor que cero",
                )

        products_out_stock = []
        for item in order.items:
            cursor.execute('''
                SELECT product_name, product_stock
                FROM products 
                WHERE product_id = ?''', (item.product_id,))
            product = cursor.fetchone()

            if not product:
                raise HTTPException(
                    status_code = status.HTTP_404_NOT_FOUND,
                    detail = f"Producto con id [{item.product_id}] no encontrado"
                )

            # Validation for minimum stock
            if product["product_stock"] < item.quantity:
                products_out_stock.append((item.product_id, product["product_name"]))

        if products_out_stock:
            raise HTTPException(
                status_code = status.HTTP_400_BAD_REQUEST,
                detail = f"Para generar el pedido no hay sufiente stock de: {products_out_stock}"
            )

        with conn:
            cursor.execute("INSERT INTO orders (order_date) VALUES (?)", (datetime.now(),))
            order_id = cursor.lastrowid

            for item in order.items:
                cursor.execute('''
                    INSERT INTO order_items (order_id, product_id, quantity)
                    VALUES (?, ?, ?)
                ''', (order_id, item.product_id, item.quantity))

                new_stock = product["product_stock"] - item.quantity

                cursor.execute('''
                    UPDATE products
                    SET product_stock = ?
                    WHERE product_id = ?
                ''', (new_stock, item.product_id))

        return {
            "order_id": order_id,
            "message": "Pedido creado correctamente",
            "items": [
                {"product_id": item.product_id, "cantidad": item.quantity}
                for item in order.items
            ],
        }

    except HTTPException as e:
        raise e
    except Exception as e:
        conn.rollback()  # Undo changes in case unexpected error
        raise HTTPException(
            status_code = status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail = f"Error inesperado: {str(e)}"
        )
    finally:
        conn.close()


# Endpoint to list all orders with validation and secured by user authentication by JWT
@router.get("/", response_model=List[OrderResponse])
async def get_orders(current_user: dict = Depends(get_current_user)):
    if current_user["user_role"] != "admin":
        raise HTTPException(
            status_code = status.HTTP_403_FORBIDDEN,
            detail = "No tienes permisos para realizar esta accion"
        )

    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT o.order_id, o.order_date, oi.product_id, oi.quantity, p.product_name, p.product_price
            FROM orders o
            JOIN order_items oi ON o.order_id = oi.order_id
            JOIN products p ON oi.product_id = p.product_id
        ''')
        orders = cursor.fetchall()

        # Add format for exit data
        order_dict = {}
        for row in orders:
            if row['order_id'] not in order_dict:
                order_dict[row['order_id']] = {
                    "order_id": row['order_id'],
                    "order_date": row['order_date'],
                    "items": [],
                    "total_price": 0.0
                }
            # Add item to order
            order_dict[row['order_id']]['items'].append({
                "product_id": row['product_id'],
                "product_name": row['product_name'],
                "quantity": row['quantity'],
                "price": row['product_price']
            })

            order_dict[row['order_id']]['total_price'] += row['product_price'] * row['quantity']

        return list(order_dict.values())

    except Exception as e:
        raise HTTPException(
            status_code = status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail = f"Error inesperado: {str(e)}"
        )
    finally:
        conn.close()
