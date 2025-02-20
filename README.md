<h1 align="center"> FastAPI Project </h1>

<p align="left">
<img src="https://img.shields.io/badge/STATUS-EN%20DESAROLLO-green">
</p>

Este proyecto es una API desarrollada con FastAPI que permite gestionar productos y pedidos. La API está dividida en dos módulos principales:

    API 1: Gestión de Productos:

        Permite listar, crear, actualizar nombre e stock y eliminar productos.

        Cada producto tiene un ID, nombre, precio y stock.

    API 2: Gestión de Pedidos:

        Permite crear y listar pedidos.

        Cada pedido incluye los productos solicitados y actualiza el stock automáticamente.

La API utiliza SQLite como base de datos y está protegida por un sistema de autenticación basado en JWT (JSON Web Tokens) y algunas validaciones adicionales.

## Características Principales

- POST /internal/api/v1/aut/login -> Autentificacion inicial, el usuario introduce sus credenciales y se obtiene el token JWT en caso favorable.
- GET /internal/api/v1/productos/ -> Lista todos los productos de almacenados.
- POST /internal/api/v1/productos -> Crea un nuevo producto. Requiere autenticación de administrador.
- PUT /internal/api/v1/productos/{id}/nombre -> Actualiza el nombre del producto. Requiere autenticación de administrador.
- PUT /internal/api/v1/productos/{id}/stock -> Actualiza el stock del producto. Requiere autenticación de administrador.
- DEL /internal/api/v1/productos/{id} -> Elimina un producto. Requiere autenticación de administrador.
- POST /internal/api/v1/pedidos/ -> Crea un nuevo pedido. Verifica el stock de los productos y lo actualiza automáticamente.
- GET /internal/api/v1/pedidos/ -> Devuelve la lista de pedidos registrados, incluyendo los detalles de los productos y el precio total.
- Documentación Automática -> La API incluye documentación interactiva generada automáticamente con Swagger una vez esta ejecutada.

## Requisitos Previos

Antes de ejecutar el proyecto, asegúrate de tener instalado lo siguiente:

- Python 3.7 o superior.
- Pip (gestor de paquetes de Python).
- Sqlite3
- Uvicorn
- Postman (opcional, usado para las pruebas) 

## Sigue estos pasos para configurar y ejecutar el proyecto en tu entorno local:

1. Clona el repositorio:
   ```bash
   git clone https://github.com/ykonyk/Caso-practico-con-FastAPI.git
   cd Caso-practico-con-FastAPI
   
2. Crea un entorno virtual (opcional):
   ```bash
   python -m venv venv
   source venv/bin/activate  # En Windows: venv\Scripts\activate
   
3. Instala las dependencias:
   ```bash
   pip install -r requirements.txt

4. Crea la base de datos:
   ```bash
   python database.py

5. Inicia el servidor de desarrollo:
   ```bash
   uvicorn main:app --reload
   
6. Accede a la documentación interactiva de la API:

    - Swagger UI: http://127.0.0.1:8000/docs

    - ReDoc: http://127.0.0.1:8000/redoc

## Ejemplos de uso
   ```bash
1. Obtener un Token:
{
    "user_name": "admin",
    "user_password": "password123",
    "user_role": "admin"
}
->Respuesta servidor:
{
    "access_token": "eyJhbIiwiZXhwIjoxNzQwMDA1Mjg1fQ.ZaLqFos3asOvUzppEuxMuJY2OxcJSmUGLECU6Z5gcJw",
    "token_type": "bearer"
}


2. Crear un Producto
{
    "product_name": "Producto 3", 
    "product_price": 8, 
    "product_stock": 35
}
->Respuesta servidor:
{
    "product_id": 3,
    "product_name": "Producto 3",
    "product_price": 8.0,
    "product_stock": 35
}


3. Crear un Pedido
{
  "items": [
    {"product_id": 1, "quantity": 3},
    {"product_id": 2, "quantity": 3},
    {"product_id": 3, "quantity": 3}
  ]
}
->Respuesta servidor:
{
    "order_id": 3,
    "message": "Pedido creado correctamente",
    "items": [
        {
            "product_id": 1,
            "cantidad": 3
        },
        {
            "product_id": 2,
            "cantidad": 3
        },
        {
            "product_id": 3,
            "cantidad": 3
        }
    ]
}
