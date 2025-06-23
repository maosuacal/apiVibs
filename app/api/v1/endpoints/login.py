from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session, select

from app.core.auth import create_access_token
from app.dependencies.database import get_session
from app.models.model_user import LoginRequest,User
from app.schemas.schema_user import LoginRequestOut
from app.services.service_user import send_email

from app.services.service_user import authenticate_user

# router para los endpoints de user
router = APIRouter(prefix="/auth", tags=["auth"])

@router.post("/login")
async def login(request: LoginRequest, db: Session = Depends(get_session)):
    # Buscar el usuario en la base de datos
    statement = select(User).where(User.username  == request.username)
    db_user = db.exec(statement).first()

    if not db_user:
        print("Usuario no encontrado.")
        raise HTTPException(status_code=401, detail="Usuario no encontrado")

    if not db_user.verify_password(request.password):
        raise HTTPException(status_code=402, detail="Contraseña incorrecta")
    
    if not db_user.status == 1:
        print("Usuario inactivo.")
        raise HTTPException(status_code=402, detail="Usuario Inactivo o bloqueado")
    
    if not db_user.email_verify == 1:
        user = User(**db_user.__dict__)
        await send_email(user)  
        raise HTTPException(status_code=202, detail="Por favor verifica tu correo para poder acceder")

    if db_user.role not in ("SYSTEM_USER" , "APP_USER"):
        raise HTTPException(status_code=403, detail="Acceso denegado, role inválido")

    access_token = create_access_token(data={"sub": db_user.username, "role": db_user.role})
    
    return {"access_token": access_token, "token_type": "bearer", "user": LoginRequestOut.from_orm(db_user)}
