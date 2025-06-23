from sqlmodel import Field, SQLModel, Relationship
from typing import Optional
from datetime import datetime

class ProductBase(SQLModel):
    company_id: int
    category_id: int
    product_code: str
    product_name: str
    description: str
    points_value: int
    monetary_value: float
    stock_quantity: int
    image_url: str
    status: int = 0
    
class Products(SQLModel, table=True):
    __table_args__ = {"schema": "glum"}
    id: int = Field(default=None, primary_key=True)
    company_id: int = Field(..., min_length=1, max_length=10000)
    category_id: int = Field(foreign_key="glum.categories.id")
    product_code: str = Field(..., index=True)
    product_name: str = Field(..., min_length=5, max_length=100)
    description: str = Field(..., min_length=2, max_length=250)
    points_value: int = Field(..., min_length=1, max_length=999)
    monetary_value: float = Field(..., min_length=1.00, max_length=9999.99)
    stock_quantity: int = Field(..., min_length=1, max_length=9999)
    image_url: str = Field(...,  min_length=5, max_length=512)
    status: int = Field(default=0, ge=0, le=9)
    currency_id: int = Field(default=1, ge=1, le=9)
    created_at: datetime = Field(default_factory=datetime.utcnow)  # Fecha de creación
    updated_at: datetime = Field(default_factory=datetime.utcnow)  # Fecha de actualización

    category: Optional["Categories"] = Relationship(back_populates="products")

class ProductSummary(SQLModel):
    id: int
    product_name: str
    category_id: int
    category_name: str
    points_value: int
    image_url: str

class ProductCreate(ProductBase):
    pass

class ProductRead(ProductBase):
    id: int
    created_at: datetime
    updated_at: datetime

class ProductUpdate(SQLModel):
    product_code: Optional[str] = None
    product_name: Optional[str] = None
    description: Optional[str] = None
    points_value: Optional[int] = None
    monetary_value: Optional[float] = None
    stock_quantity: Optional[int] = None
    image_url: Optional[str] = None
    status: Optional[int] = None


from app.models.model_category import Categories
Products.update_forward_refs()

"""
Consulta de BD para mostrar los productos
select p.id, p.product_name, p.category_id, c.category_name, p.points_value, p.image_url
from products p inner join categories c on (c.id = p.category_id) 
inner join companies c2 on (C2.id = C.company_id)
where C.company_id = 2
"""
