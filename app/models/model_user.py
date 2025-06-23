from sqlmodel import SQLModel, Field
from datetime import datetime
from typing import Optional
from pydantic import EmailStr, BaseModel
from app.core.auth import hash_password
from enum import Enum
from passlib.context import CryptContext

# Contexto de hashing para las contraseñas
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

class UserRole(str, Enum):
    APP_USER = "APP_USER"
    SYSTEM_USER = "SYSTEM_USER"
    APP_CLIENT = "APP_CLIENT"


class UserBase(SQLModel):
    username: str = Field(..., min_length=2, max_length=100) # Es el mismo mail
    email: EmailStr = Field(..., index=True)  # Valida formato de email, ademas es obligatorio
    phone_number: str = Field(..., min_length=10, max_length=20)  # Número de teléfono obligatorio
    first_name: str = Field(..., min_length=2, max_length=100)
    last_name: str = Field(..., min_length=2, max_length=100)
    login_attempts: int = Field(default=0, ge=0, le=9)
    created_at: datetime = Field(default_factory=datetime.utcnow)  # Fecha de creación
    updated_at: datetime = Field(default_factory=datetime.utcnow)  # Fecha de actualización
    role: UserRole = Field(default=UserRole.APP_USER) # El tipo de usuario: Uno es un usuario de LAUZ y el otro tipo es un usuario de sistema back

class User(UserBase, table=True):
    __table_args__ = {"schema": "glum"}
    id: int = Field(default=None, primary_key=True)
    password_hash: str  # Se almacena hasheado
    email_verify: Optional[int] = Field(default=0, ge=0, le=9)  # Si el email está verificado (proceso que debo revisar)
    user_type: Optional[int] = Field(default=8, ge=0, le=9)
    status: Optional[int] = Field(default=1,ge=0, le=9)
    must_change_password: Optional[bool] = Field(default=False)

    # Método para verificar la contraseña ingresada
    def verify_password(self, password: str) -> bool:
        return pwd_context.verify(password, self.password_hash)


class LoginRequest(SQLModel):
    username: str = Field(index=True)
    password: str
    rol: str

    # Método para establecer la contraseña
    def set_password(self, password: str):
        self.password_hash = pwd_context.hash(password)

    # Método para verificar la contraseña
    def verify_password(self, password: str) -> bool:
        return pwd_context.verify(password, self.password_hash)

    """ NOTAS
    password_hash: Ahora en la BD solo se guardará el hash de la contraseña, no el texto plano.
    set_password(): Genera un hash seguro a partir de una contraseña y lo almacena.
    verify_password(): Compara la contraseña ingresada con el hash almacenado.
    """

class userPublic(UserBase):
    id: int
    email_verify: bool


class userCreate(UserBase):
    password_hash: str  # Se recibe en texto plano y se hashea antes de guardarla

    def hash_password(password: str) -> str:
        return pwd_context.hash(password)

class userUpdate(SQLModel):
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    #username: Optional[str] = None
    #email: Optional[EmailStr] = None # No puede existir modificación de este dato ya que es una llave.
    #phone: Optional[str] = None # No debe existir modificación de este dato ya que es una llave.
    password: Optional[str] = None  # Solo si el usuario desea cambiarla
    #email_verify: Optional[bool] = None

