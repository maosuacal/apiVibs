from fastapi import HTTPException, status, Query
from sqlmodel import Session, select
from typing import Optional, Annotated
from datetime import datetime, timedelta
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

from app.core.config import settings
from app.models.model_user import User
from app.schemas.schema_user import userCreate, userPublic, userUpdate
from app.core.auth import hash_password, verify_password
from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# Crear una nueva cuenta de usuario
def create_user(db: Session, user_create: userCreate) -> User:

    new_user = User(**user_create.dict())

    db.add(new_user)
    db.commit()
    db.refresh(new_user)

     # Enviar el correo de verificación después de crear el usuario
    send_verification_email(new_user.email, new_user.first_name)

    return new_user


# Consultar todos los usuarios
def get_users(db: Session, offset: int = 0, limit: int = 100):
    query = db.query(User)
    return query.all()


# Función para obtener una cuenta por id
def get_user_id(db: Session, id: int):
    return db.get(User, id)


# Función para obtener una cuenta por correo electrónico
def get_user_by_email(db: Session, email: str) -> User | None:
    stmt = select(User).where(User.email == email)
    db_user = db.exec(stmt).first()
    return db_user


# Función para obtener una cuenta por numero celular
def get_user_by_phone(db: Session, phone: str) -> User | None:
    stmt = select(User).where(User.phone_number == phone)
    db_user = db.exec(stmt).first()
    return db_user


# Función para actualizar una cuenta de usuario
def update_user(db: Session, user_id: int, user_update: userUpdate) -> User | None:
 
    db_user = db.get(User, user_id)
    
    if not db_user:
        return None
    
    # Actualizar los campos que se proporcionan en user_update
    user_data = user_update.model_dump(exclude_unset=True)  # Excluir los campos no proporcionados
    
    # Hashear el password si viene en la actualización (cambio de clave)
    if "password" in user_data:
        user_data["password"] = hash_password(user_data["password"])

    # Actualizar los valores de la cuenta
    for key, value in user_data.items():
        setattr(db_user, key, value)

    db_user.updated_at = datetime.utcnow()
    
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    
    return db_user


# Autenticación de usuario en el endpoint de login
def authenticate_user(db: Session, username: str, password: str):
    db_user = db.query(User).filter(User.username == username).first()
    if not db_user or not db_user.verify_password(password):
        return None
    
    if not db_user.verify_password(password):
        return None
    
    return db_user

async def send_email(user: User):
    subject = "Verificación de Email"
    body = f"Hola, {user.email}. Haz clic en el siguiente enlace para verificar tu cuenta: [enlace de verificación]"
    send_verification_email(user.email, user.first_name)
    return {"message": "Correo de verificación enviado"}

# Función para enviar un correo de verificación
def send_verification_email(user_email: str, user_name: str):
    # Datos del correo
    sender_email = settings.USER_EMAIL_NOTIFICATIONS
    sender_password = settings.PASSWORD_EMAIL_NOTIFICATIONS
    smtp_server = settings.MAIL_HOST
    smtp_port = settings.MAIL_PORT

    # Crear el mensaje
    msg = MIMEMultipart()
    msg['From'] = sender_email
    msg['To'] = user_email
    msg['Subject'] = 'Verifica tu dirección de correo electrónico'

    # Cuerpo del correo
    body = f"""
    Hola {user_name},

    Gracias por registrarte. Por favor, haz clic en el siguiente enlace para verificar tu dirección de correo electrónico:

    http://127.0.0.1:8080/users/users/verify-email/{user_email}  # URL de verificación

    Si no solicitaste este correo, puedes ignorarlo.

    Saludos,
    El equipo de tu aplicación
    """
    
    msg.attach(MIMEText(body, 'plain'))

    try:
        # Conectar al servidor SMTP de Gmail y enviar el correo
        server = smtplib.SMTP(smtp_server, smtp_port)
        server.starttls()  # Usar TLS para la seguridad de la conexión
        server.login(sender_email, sender_password)
        server.sendmail(sender_email, user_email, msg.as_string())
        server.quit()
        print(f"Correo de verificación enviado a {user_email}")
    except Exception as e:
        print(f"Error al enviar el correo: {e}")
        raise HTTPException(status_code=500, detail="Error al enviar el correo de verificación.")



""" Función para enviar el correo electrónico
def send_verification_email_bkp(to_email, subject, body):
    from_email = settings.USER_EMAIL_NOTIFICATIONS
    from_password = settings.PASSWORD_EMAIL_NOTIFICATIONS
    
    # Configurar el servidor SMTP
    smtp_server = settings.MAIL_HOST
    smtp_port = settings.MAIL_PORT

    # Crear el mensaje
    message = MIMEMultipart()
    message["From"] = from_email
    message["To"] = to_email
    message["Subject"] = subject
    message.attach(MIMEText(body, "plain"))

    try:
        # Enviar el correo
        server = smtplib.SMTP(smtp_server, smtp_port)
        server.starttls()  # Usar TLS
        server.login(from_email, from_password)
        server.sendmail(from_email, to_email, message.as_string())
        server.close()
        print("Correo enviado correctamente.")
    except Exception as e:
        print(f"Ocurrió un error: {e}") """ 