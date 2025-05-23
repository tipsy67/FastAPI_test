from sqlalchemy import Column, Numeric, Integer, Boolean, Float, String, ForeignKey
from sqlalchemy.orm import relationship

from app.backend.db import Base


class Product(Base):
    __tablename__ = "product"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String)
    description = Column(String)
    slug = Column(String, unique=True, index=True)
    is_active = Column(Boolean, default=True)
    price = Column(Numeric)
    image_url = Column(String, nullable=True)
    stock = Column(Integer)
    rating = Column(Float)
    category_id = Column(Integer, ForeignKey('category.id'))

    cat = relationship('Category', backref='products', uselist=False)

