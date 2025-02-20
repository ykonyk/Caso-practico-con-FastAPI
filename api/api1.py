from fastapi import HTTPException, Depends, status, APIRouter
from pydantic import BaseModel
from .auth import get_db_connection, get_current_user


# Router URL for authentication for "productos"
router = APIRouter(prefix = "/internal/api/v1/productos", tags = ["productos"])


class Product(BaseModel):
    product_name: str
    product_price: float
    product_stock: int

class ProductUpdateStock(BaseModel):
    product_stock: int

class ProductUpdateName(BaseModel):
    product_name: str


# Function to list all the products stored in DB
@router.get("/")
async def get_products():
    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        cursor.execute("SELECT * FROM products")

        productos = cursor.fetchall()
        conn.close()

        return [dict(producto) for producto in productos]
    
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(
            status_code = status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail = f"Error inesperado: {str(e)}")


# Create new product with validation and secured by user authentication by JWT
@router.post("/", status_code=status.HTTP_201_CREATED)
async def product_create(product: Product, current_user: dict = Depends(get_current_user)):
    if current_user["user_role"] != "admin":
        raise HTTPException(
            status_code = status.HTTP_403_FORBIDDEN,
            detail = "No tienes permisos para realizar esta accion"
        )

    try:
        if product.product_stock < 0:
            raise HTTPException(
                status_code = status.HTTP_400_BAD_REQUEST,
                detail = "El stock no puede ser negativo"
            )
        
        conn = get_db_connection()
        cursor = conn.cursor()

        cursor.execute('''
            INSERT INTO products (product_name, product_price, product_stock)
            VALUES (?, ?, ?)
        ''', (product.product_name, product.product_price, product.product_stock))

        producto_id = cursor.lastrowid

        conn.commit()
        conn.close()

        return {
            "product_id": producto_id,
            "product_name": product.product_name,
            "product_price": product.product_price,
            "product_stock": product.product_stock
        }
    
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(
            status_code = status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail = f"Error inesperado: {str(e)}")


# Update the product stock with model validation limiting nagative cases 
@router.put("/{id}/stock")
async def stock_update(id: int, stock_update: ProductUpdateStock, current_user: dict = Depends(get_current_user)):
    if current_user["user_role"] != "admin":
        raise HTTPException(
            status_code = status.HTTP_403_FORBIDDEN,
            detail = "No tienes permisos para realizar esta accion"
        )

    try:
        if stock_update.product_stock < 0:
            raise HTTPException(
                status_code = status.HTTP_400_BAD_REQUEST,
                detail = "El stock no puede ser negativo"
            )
        
        conn = get_db_connection()
        cursor = conn.cursor()

        cursor.execute("SELECT product_id FROM products WHERE product_id = ?", (id,))
        if not cursor.fetchone():
            raise HTTPException(
                status_code = status.HTTP_404_NOT_FOUND,
                detail = "Producto no encontrado"
            )
        
        cursor.execute('''
            UPDATE products
            SET product_stock = ?
            WHERE product_id = ?
        ''', (stock_update.product_stock, id))

        conn.commit()
        conn.close()

        return {"product_id": id, "product_stock": stock_update.product_stock}

    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(
            status_code = status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail = f"Error inesperado: {str(e)}")


# Update the product name with model validation and secured by user authentication by JWT
@router.put("/{id}/nombre")
async def name_update(id: int, name_update: ProductUpdateName, current_user: dict = Depends(get_current_user)):
    if current_user["user_role"] != "admin":
        raise HTTPException(
            status_code = status.HTTP_403_FORBIDDEN,
            detail = "No tienes permisos para realizar esta accion"
        )

    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        cursor.execute("SELECT product_id FROM products WHERE product_id = ?", (id,))
        if not cursor.fetchone():
            raise HTTPException(
                status_code = status.HTTP_404_NOT_FOUND,
                detail = "Producto no encontrado"
            )

        cursor.execute('''
            UPDATE products
            SET product_name = ?
            WHERE product_id = ?
        ''', (name_update.product_name, id))

        conn.commit()
        conn.close()

        return {"product_id": id, "product_name": name_update.product_name}

    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(
            status_code = status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail = f"Error inesperado: {str(e)}")


# Delete product secured by user authentication by JWT
@router.delete("/{id}")
async def product_delete(id: int, current_user: dict = Depends(get_current_user)):
    if current_user["user_role"] != "admin":
        raise HTTPException(
            status_code = status.HTTP_403_FORBIDDEN,
            detail = "No tienes permisos para realizar esta accion"
        )

    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        cursor.execute("SELECT product_id FROM products WHERE product_id = ?", (id,))
        if not cursor.fetchone():
            raise HTTPException(
                status_code = status.HTTP_404_NOT_FOUND,
                detail = "Producto no encontrado"
            )

        cursor.execute("DELETE FROM products WHERE product_id = ?", (id,))
        conn.commit()

        return {"message": f"Producto con id {id} eliminado correctamente"}

    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(
            status_code = status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail = f"Error inesperado: {str(e)}")
