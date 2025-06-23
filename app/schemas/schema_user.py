from pydantic import BaseModel, EmailStr
from typing import Optional
from datetime import datetime
from enum import Enum

class UserRole(str, Enum):
    SYSTEM_USER = "SYSTEM_USER"
    APP_USER = "APP_USER"
    APP_CLIENT = "APP_CLIENT"

# Esquema base que contiene los campos comunes
class userBase(BaseModel):
    first_name: str
    last_name: str
    username: str
    email: EmailStr  # Utiliza el tipo EmailStr para validación
    phone_number: str
    role: UserRole = UserRole.APP_USER  # El tipo de usuario: Uno es un usuario de GLUM y el otro tipo SYSTEM_USER es un usuario de sistema back


# Esquema para la creación de cuentas (se recibe la contraseña en texto plano)
class userCreate(userBase):
    password_hash: str  # Contraseña recibida en texto plano


# Esquema para la actualización de cuentas (campos opcionales)
class userUpdate(BaseModel):
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    #username: Optional[str] = None
    #email: Optional[EmailStr] = None
    #phone: Optional[str] = None
    password: Optional[str] = None  # La contraseña puede actualizarse


# Esquema para la respuesta pública (sin información sensible como la contraseña)
class userPublic(userBase):
    id: int
    email_verify: bool  # Si el correo está verificado
    created_at: datetime  # Fecha de creación
    updated_at: datetime  # Fecha de última actualización
    #username: str
    #name:str
    #last_name: str
    #phone: str
    class Config:
        orm_mode = True  # This ensures that the model works with SQLModel


# Esquema para la respuesta completa, incluye la contraseña en caso de que sea necesario
class userFull(userPublic):
    password: str  # Solo para casos en los que necesitemos devolver la contraseña, no recomendable


class LoginRequestOut(BaseModel):
    username: str
    role: str

    class Config:
        orm_mode = True  # Esto permite la conversión de objetos SQLAlchemy/SQLModel en modelos Pydantic
        from_attributes = True  # Habilitar la conversión desde el ORM directamente

        