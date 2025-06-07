from sqlalchemy import Column, Integer, ForeignKey, Boolean, DateTime, String
from sqlalchemy.orm import relationship

from app.backend.db import Base


class Review(Base):
    __tablename__ = 'review'
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey('user.id'))
    product_id = Column(Integer, ForeignKey('product.id'))
    comment = Column(String)
    comment_date = Column(DateTime)
    grade = Column(Integer)
    is_active = Column(Boolean, default=True)

    product = relationship('Product', back_populates='reviews', uselist=False)
    user = relationship('User', back_populates='reviews', uselist=False)