from pydantic import BaseModel


class CreateCategory(BaseModel):
    parent_id: int | None = None
    name: str


class CreateProduct(BaseModel):
    name: str
    description: str
    price: float
    image_url: str
    stock: int
    category: int

class CreateUser(BaseModel):
    first_name: str
    last_name: str
    username: str
    email: str
    password: str
