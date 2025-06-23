from datetime import datetime, timedelta
from typing import Optional
from jose import JWTError, jwt
from passlib.context import CryptContext
from app.core.config import settings
from datetime import timedelta


# Clave secreta (mejor cargar desde variables de entorno)
APP_TOKEN_SECRET_KEY = settings.TOKEN_GLUM.encode("utf-8")
APP_TOKEN_ALGORITHM = settings.ALGORITM
ACCESS_TOKEN_EXPIRE_MINUTES = int(settings.TIME_EXP_WSGLUM)  # Duración del token en minutos

# Configurar hashing de contraseñas con bcrypt
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# Función para crear un nuevo JWT
def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    #if expires_delta:
    #    expire = datetime.utcnow() + expires_delta
    #else:
    #   expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    
    #to_encode["exp"] = expire
    #to_encode.update({"exp": int(expire.timestamp())})
    encoded_jwt = jwt.encode(to_encode, APP_TOKEN_SECRET_KEY, APP_TOKEN_ALGORITHM)
    #encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


def hash_password(password: str) -> str:
    """Devuelve la contraseña hasheada"""
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verifica si la contraseña ingresada coincide con la almacenada"""
    return pwd_context.verify(plain_password, hashed_password)


# Función para decodificar el JWT
def decode_access_token(token: str):
    try:
        payload = jwt.decode(token, APP_TOKEN_SECRET_KEY, algorithms=[APP_TOKEN_ALGORITHM])
        
        return payload
    except JWTError:
        return None