from fastapi import HTTPException, Depends, status, APIRouter
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from datetime import datetime, timedelta
from pydantic import BaseModel
from passlib.hash import sha256_crypt
import sqlite3


# Router URL for authentication
router = APIRouter(prefix="/internal/api/v1/aut", tags=["auth"])

# Route for where is security token is obtained in this case "login"
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/internal/api/v1/aut/login")


# This should be hiden inside production variables, critical info
SECRET_KEY = "mango"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 5


# Pydantic models for data validation
class LoginRequest(BaseModel):
    user_name: str
    user_password: str
    user_role: str

class Token(BaseModel):
    access_token: str
    token_type: str


# Establish shop DB conection
def get_db_connection():
    try:
        conn = sqlite3.connect("shop.db")
        conn.row_factory = sqlite3.Row
        return conn

    except sqlite3.Error as e:
        raise HTTPException(status_code = 500, detail = f"Error de base de datos: {str(e)}")


# Create the JWT token to assure the user identity
def create_access_token(data: dict):
    encode = data.copy()
    expire = datetime.now() + timedelta(minutes = ACCESS_TOKEN_EXPIRE_MINUTES)
    encode.update({"exp": expire})
    encoded_jwt = jwt.encode(encode, SECRET_KEY, algorithm = ALGORITHM)
    return encoded_jwt


# Autentificate and obtain user information from the JWT token
# async def, allows FastAPI handle multiple requests concurrently more efficiently.
async def get_current_user(token: str = Depends(oauth2_scheme)):
    credentials_exception = HTTPException(
        status_code = status.HTTP_401_UNAUTHORIZED,
        detail = "No se han podido validar las credenciales proporcionadas",
        headers = {"WWW-Authenticate": "Bearer"},
    )
    try:
        decoded_jwt = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username = decoded_jwt.get("user_name")
        role = decoded_jwt.get("user_role")
        if username is None or role is None:
            raise credentials_exception
        return {"user_name": username, "user_role": role}
    except JWTError:
        raise credentials_exception


# Final user autentification comparing given name, passwd and role to stored in DB
@router.post("/login", response_model = Token)
async def login(login_request: LoginRequest):
    username = login_request.user_name
    password = login_request.user_password
    role = login_request.user_role

    if not username or not password or not role:
        raise HTTPException(
            status_code = status.HTTP_400_BAD_REQUEST,
            detail = "Campos de usuario, contraseña y rol son obligatorios"
        )

    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute("SELECT * FROM users WHERE user_name = ?", (username,))
        user = cursor.fetchone()

        if not user:
            raise HTTPException(
                status_code = status.HTTP_401_UNAUTHORIZED,
                detail = "Usuario no encontrado"
            )

        if not sha256_crypt.verify(password, user["user_password"]):
            raise HTTPException(
                status_code = status.HTTP_401_UNAUTHORIZED,
                detail = "Contraseña incorrecta"
            )

        if role != user["user_role"]:
            raise HTTPException(
                status_code = status.HTTP_401_UNAUTHORIZED,
                detail = "Rol incorrecto"
            )

        access_token = create_access_token(
            data = {"user_name": user["user_name"], "user_role": user["user_role"]})

        return {"access_token": access_token, "token_type": "bearer"}

    except sqlite3.Error as e:
        raise HTTPException(
            status_code = status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail = f"Error inesperado: {str(e)}"
        )
    finally:
        conn.close()
