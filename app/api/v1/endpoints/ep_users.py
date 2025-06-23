from datetime import datetime, timedelta
from fastapi import APIRouter, Depends, HTTPException, Path, Query, Security, status
from fastapi.responses import HTMLResponse
from sqlmodel import Session, select
from typing import List, Annotated, Optional
from fastapi.security import OAuth2PasswordBearer


from app.core.auth import create_access_token, hash_password
from app.core.validate_token import get_current_user, validate_token_payload
from app.dependencies.database import get_session
from app.models.model_user import User, LoginRequest
from app.schemas.schema_user import userCreate, userUpdate, userPublic, LoginRequestOut
from app.services.service_user import create_user, get_user_by_email, update_user, get_users, get_user_id, get_user_by_phone

# router para los endpoints de user
router = APIRouter(prefix="/users", tags=["users"])

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")


#Crear una cuenta de usuario
@router.post("/create", response_model=userPublic, status_code=201, summary="Crear usuario")
def create_new_user(user_create: userCreate, db: Session = Depends(get_session), current_user: dict = Depends(get_current_user),):

    if current_user.role != "SYSTEM_USER":
        raise HTTPException(status_code=403, detail="Access forbidden: Insufficient role")

    # Verificar si el usuario ya existe
    existing_user = db.query(User).filter(User.username == user_create.username).first()
    if existing_user:
        raise HTTPException(status_code=400, detail="Username already registered")

    # Hashear la contraseña del nuevo usuario
    user_create.password_hash = hash_password(user_create.password_hash)

    new_user = create_user(db, user_create)

    return new_user


#Obtener una cuenta por email**
@router.get("/users/email/{email}", response_model=userPublic, summary="Buscar usuario por email")
def get_user_email(
    email: str, 
    db: Session = Depends(get_session), 
    current_user: dict = Depends(get_current_user)):
    db_user = get_user_by_email(db, email)
    if not db_user:
        raise HTTPException(status_code=404, detail="user not found")
    return db_user


#Obtener una cuenta por nùmero celular**
@router.get("/users/phone/{phone}", response_model=userPublic, summary="Buscar usuario por nùmero celular")
def get_user_phone(
    phone: str, 
    db: Session = Depends(get_session), 
    current_user: dict = Depends(get_current_user)):
    db_user = get_user_by_phone(db, phone)
    if not db_user:
        raise HTTPException(status_code=404, detail="user not found")
    return db_user


#Consulta una cuenta por Id
@router.get("/users/{user_id}", response_model=userPublic, summary="Buscar usuario por ID")
def read_user(
    user_id: int, 
    db: Session = Depends(get_session),
    current_user: dict = Depends(get_current_user)):
    
    user = get_user_id(db, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="user not found")
    return user


# Consulta todas las cuentas
@router.get("/users", response_model=list[userPublic], summary="Consultar todos los usuarios")
def read_users(
    db: Session = Depends(get_session), 
    current_user: dict = Depends(get_current_user), 
    offset: int = 0, limit: Annotated[int, Query(le=100)] = 100):
    
    return get_users(db, offset, limit)


#Actualizar una cuenta de usuario**
@router.put("/update/{user_id}", response_model=userPublic, summary="Actualizar datos de usuario")
def update_existing_user(user_id: int, user_update: userUpdate, db: Session = Depends(get_session)):
    db_user = update_user(db, user_id, user_update)
    if db_user is None:
        raise HTTPException(status_code=404, detail="user not found")
    return db_user


#login de usuarios
@router.post("/login")
async def login( request: LoginRequest, db: Session = Depends(get_session), app_auth_token: Optional[str] = Security(oauth2_scheme, scopes=[]),):
    
    statement = select(User).where(User.username == request.username)
    db_user = db.exec(statement).first()

    if not db_user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Usuario no encontrado")

    if not db_user.verify_password(request.password):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Contraseña incorrecta")
    
    if not db_user.status == 1:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Usuario Inactivo o bloqueado")
    
    """ if not db_user.email_verify == 1:
        user = User(**db_user.__dict__)
        await send_email(user)  
        raise HTTPException(status_code=status.HTTP_202_ACCEPTED, detail="Por favor verifica tu correo para poder acceder") """

    # --- Validación específica para APP_USER (con token del header) ---
    if request.rol == "APP_USER":

        if not app_auth_token:
            
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Para APP_USER, se requiere un token de autorización de aplicación en el encabezado."
            )
        
        try:
            app_token_payload = validate_token_payload(app_auth_token)
            
        except HTTPException as e:
            # Re-lanza la excepción si tu función validate_token_payload ya maneja los errores
            print(f"ERROR: Falló la validación del token de aplicación: {e.detail}")
            raise e

        except Exception as e:
            # Captura cualquier otro error inesperado durante la validación
            print(f"ERROR INESPERADO: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Error inesperado al validar el token de aplicación: {e}"
            )
            
            print(f"Token de aplicación (APP_USER) presente y validado (DEBUG): {app_auth_token[:20]}...")
    
    # --- Validación final del rol (existente) ---
    if request.rol != db_user.role:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"Acceso denegado: El rol solicitado ('{request.rol}') no coincide con el rol del usuario en la base de datos ('{db_user.role}')."
        )

    # --- Generación y retorno del token de acceso para el usuario ---
    access_token = create_access_token(data={"sub": db_user.username, "role": db_user.role})
    return {"message": "Usuario autenticado exitosamente", "user": LoginRequestOut.from_orm(db_user)}
    

# Validar confirmacion de email
@router.get("/verify-email/{email}")
async def verify_email(email: str, db: Session = Depends(get_session)):
    # Aquí se debe actualizar el campo `email_verify` de la base de datos
    db_user = db.query(User).filter(User.email == email).first()
    if db_user:
        db_user.email_verify = True
        db.commit()
        return HTMLResponse(content="""
            <!DOCTYPE html>
            <html lang="es">
            <head>
                <meta charset="UTF-8">
                <title>Correo Verificado</title>
                <style>
                    body {
                        background-color: #1B2627;
                        color: white;
                        font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                        display: flex;
                        flex-direction: column;
                        justify-content: center;
                        align-items: center;
                        height: 100vh;
                        margin: 0;
                    }
                    h1 {
                        font-size: 2.5rem;
                        margin-bottom: 20px;
                    }
                    p {
                        font-size: 1.2rem;
                        margin-bottom: 30px;
                    }
                    a.button {
                        padding: 12px 25px;
                        background-color: #4CAF50;
                        color: white;
                        text-decoration: none;
                        font-weight: bold;
                        border-radius: 8px;
                        transition: background 0.3s ease;
                    }
                    a.button:hover {
                        background-color: #45a049;
                    }
                </style>
            </head>
            <body>
                <h1>¡Correo verificado con éxito!</h1>
                <p>Tu cuenta ha sido activada. Ahora puedes iniciar sesión.</p>
                <a href="http://127.0.0.1:8000/login" class="button">Iniciar sesión</a>
            </body>
            </html>
        """)
    else:
        return HTMLResponse(content="""
            <html>
                <body style="background:#1B2627; color:white; display:flex; align-items:center; justify-content:center; height:100vh;">
                    <h2>No se pudo verificar el correo.</h2>
                </body>
            </html>
        """, status_code=404)