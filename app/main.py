from fastapi import FastAPI, Depends
from app.core.database import create_db_and_tables
from app.api.v1.endpoints import ep_products, ep_users, login
from fastapi.security import OAuth2PasswordBearer

app = FastAPI()

@app.on_event("startup")
def on_startup():
    create_db_and_tables()

# Incluir los routers de los endpoints
app.include_router(ep_users.router, prefix="/users", tags=["users"])
app.include_router(ep_products.router, prefix="/products", tags=["products"])
#app.include_router(login.router, prefix="/auth", tags=["auth"])
app.include_router(login.router, tags=["auth"])
