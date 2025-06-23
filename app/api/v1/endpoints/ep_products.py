from datetime import datetime
from fastapi import APIRouter, HTTPException, Depends, Query
from sqlmodel import Session, select, col
from typing import List
from app.models.model_product import Products, ProductCreate, ProductRead, ProductUpdate, ProductSummary
from app.dependencies.database import get_session
from app.models.model_category import Categories
from app.core.validate_token import get_current_user


# router para los endpoints de user
router = APIRouter(prefix="/products", tags=["products"])

# Retorna todos los productos de una compañìa
@router.get("/summary", response_model=List[ProductSummary], summary="Mostrar productos de una compañìa")
def list_products_summary(company_id: int = Query(...), session: Session = Depends(get_session),current_user: dict = Depends(get_current_user)):
    statement = (
        select(
            Products.id,
            Products.product_name,
            Products.category_id,
            Categories.category_name.label("category_name"),
            Products.points_value,
            Products.image_url
        )
        .join(Categories, Categories.id == Products.category_id)
        .where(Products.company_id == company_id)
    )
    results = session.exec(statement).all()

    # Mapeo manual a ProductSummary.
    return [
        ProductSummary(
            id=r.id,
            product_name=r.product_name,
            category_id=r.category_id,
            category_name=r.category_name,
            points_value=r.points_value,
            image_url=r.image_url
        )
        for r in results
    ]

# Crear producto
@router.post("/create", response_model=ProductRead, summary="Crear producto")
def create_product(product: ProductCreate, session: Session = Depends(get_session)):
    db_product = Products(**product.dict())
    session.add(db_product)
    session.commit()
    session.refresh(db_product)
    return db_product

# Buscar producto por Id
@router.get("/{product_id}", response_model=ProductRead, summary="Buscar producto por Id")
def read_product(product_id: int, session: Session = Depends(get_session),current_user: dict = Depends(get_current_user)):
    product = session.get(Products, product_id)
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    return product

# Actualizar producto por Id
@router.put("/update/{product_id}", response_model=ProductRead, summary="Actualizar datos de un producto")
def update_product(product_id: int, product_update: ProductUpdate, session: Session = Depends(get_session),current_user: dict = Depends(get_current_user)):
    product = session.get(Products, product_id)
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    product_data = product_update.dict(exclude_unset=True)
    for key, value in product_data.items():
        setattr(product, key, value)
    product.updated_at = datetime.utcnow()
    session.add(product)
    session.commit()
    session.refresh(product)
    return product

# Borrar producto por Id
@router.delete("/delete/{product_id}", summary="Borrar un producto")
def delete_product(product_id: int, session: Session = Depends(get_session),current_user: dict = Depends(get_current_user)):
    product = session.get(Products, product_id)
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    session.delete(product)
    session.commit()
    return {"ok": True}

