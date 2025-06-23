# app/models/__init__.py
from .product import *
from .category import *
from app.models.model_product import Products
from app.models.model_category import Categories

Products.update_forward_refs()
Categories.update_forward_refs()