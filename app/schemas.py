from typing import Optional

from pydantic import BaseModel


class CreateCategory(BaseModel):
    parent_id: int | None = None
    name: str


class CreateProduct(BaseModel):
    name: str
    description: str
    price: float
    image_url: Optional[str] = None
    stock: int
    category_id: int

class CreateUser(BaseModel):
    first_name: str
    last_name: str
    username: str
    email: str
    password: str

class CreateReview(BaseModel):
    product_id: int
    comment: str
    grade: int


