# app/models/category.py
from typing import List
from sqlmodel import Relationship
from app.models.model_category import Categories
from app.models.model_product import Products

Categories.products = Relationship(
    back_populates="category"
)

Categories.update_forward_refs()
