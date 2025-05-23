from typing import Annotated

from fastapi import APIRouter, Depends, status, HTTPException
from slugify import slugify
from sqlalchemy import insert, select, update
from sqlalchemy.orm import Session


from app.backend.db_depends import get_db
from app.models import Category
from app.schemas import CreateCategory

router = APIRouter(prefix="/categories", tags=["category"])

@router.get('/')
async def get_all_categories(db: Annotated[Session, Depends(get_db)]):
    categories = db.scalars(select(Category).where(Category.is_active == True)).all()
    return categories

@router.post('/', status_code=status.HTTP_201_CREATED)
async def create_category(db:Annotated[Session, Depends(get_db)], create_cat: CreateCategory):
    db.execute(insert(Category).values(name=create_cat.name,
                                       parent_id=create_cat.parent_id,
                                       slug=slugify(create_cat.name)))
    db.commit()
    return {
        'status_code': status.HTTP_201_CREATED,
        'transaction': 'success',
    }

@router.put('/{category_slug}')
async def update_category(db: Annotated[Session, Depends(get_db)], category_slug: str, update_cat: CreateCategory):
    category = db.scalar(select(Category).where(Category.slug == category_slug))
    if category is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Category {category_slug} not found",
        )
    db.execute(update(Category).where(Category.slug == category_slug).values(
        name=update_cat.name,
        slug=slugify(update_cat.name),
        parent_id=update_cat.parent_id,
    ))
    db.commit()
    return {
        'status_code': status.HTTP_200_OK,
        'transaction': 'success',
    }


@router.delete('/{category_slug}')
async def delete_category(db: Annotated[Session, Depends(get_db)], category_slug: str):
    category = db.scalar(select(Category).where(Category.slug == category_slug))
    if category is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Category with slug {category_slug} not found")
    db.execute(update(Category).where(Category.slug == category_slug).values(is_active=False))
    db.commit()
    return {
        'status_code': status.HTTP_200_OK,
        'transaction': 'success',
    }
