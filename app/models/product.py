# app/models/product.py
from typing import Optional
from sqlmodel import Relationship
from app.models.model_product import Products
from app.models.model_category import Categories

Products.category = Relationship(
    back_populates="products"
)

Products.update_forward_refs()