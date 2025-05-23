
from sqlalchemy import Column, Boolean, Integer, ForeignKey, String
from sqlalchemy.orm import relationship

from app.backend.db import Base


class Category(Base):
    __tablename__ = 'category'
    __table_args__ = {'extend_existing': True}
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String)
    slug = Column(String, unique=True, index=True)
    is_active = Column(Boolean, default=True)
    parent_id = Column(Integer, ForeignKey('category.id'), nullable=True)

    product = relationship('Product', backref='category', uselist=True)
