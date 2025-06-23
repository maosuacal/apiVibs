from sqlmodel import SQLModel, Field, Relationship
from datetime import datetime
from typing import List, Optional

class Categories(SQLModel, table=True):
    __table_args__ = {"schema": "glum"}
    id: int = Field(default=None, primary_key=True)
    company_id: int = Field(...)
    category_name: str = Field(..., min_length=5, max_length=100)
    description: str = Field(..., min_length=2, max_length=250)
    status: int = Field(default=0, ge=0, le=9)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    products: List["Products"] = Relationship(back_populates="category")

from app.models.model_product import Products
Categories.update_forward_refs()

