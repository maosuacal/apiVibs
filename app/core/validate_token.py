from datetime import datetime, timedelta
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from sqlmodel import Session

from app.core.config import settings
from app.core.auth import create_access_token
from app.dependencies.database import get_session
from app.models.model_user import User
from app.core.config import settings


# Clave secreta (mejor cargar desde variables de entorno)
SECRET_KEY = settings.TOKEN_GLUM
ALGORITHM = settings.ALGORITM

# Crear una instancia de OAuth2PasswordBearer para extraer el token del encabezado 'Authorization'
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/login")

# Función para obtener el usuario actual desde el token JWT
def get_current_user(db: Session = Depends(get_session), token: str = Depends(oauth2_scheme)):
    
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise HTTPException(status_code=401, detail="No sub found in token")

        # Buscar el usuario en la base de datos
        db_user = db.query(User).filter(User.username == username).first()
        if db_user is None:
            raise HTTPException(status_code=401, detail="User not found")
        
        return db_user
    except JWTError:
        raise HTTPException(status_code=403, detail="Could not validate credentials")

APP_TOKEN_SECRET_KEY = settings.TOKEN_GLUM
APP_TOKEN_ALGORITHM = settings.ALGORITM

def validate_token_payload(token: str):
    try:

        payload = jwt.decode(token, APP_TOKEN_SECRET_KEY, algorithms=[APP_TOKEN_ALGORITHM])
        client_id: str = payload.get("sub")
        if client_id is None:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token de aplicación inválido: no se encontró 'sub'.")

        return payload
    except JWTError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token de autorización de aplicación inválido.")
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Error interno al validar el token: {e}")