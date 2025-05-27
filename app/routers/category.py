from typing import Annotated

from fastapi import APIRouter, Depends, status, HTTPException
from slugify import slugify
from sqlalchemy import insert, select, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.backend.db_depends import get_db
from app.models import Category
from app.schemas import CreateCategory

router = APIRouter(prefix="/categories", tags=["category"])

@router.get('/')
async def get_all_categories(db: Annotated[AsyncSession, Depends(get_db)]):
    categories = await db.scalars(select(Category).where(Category.is_active == True))
    return categories.all()

@router.post('/', status_code=status.HTTP_201_CREATED)
async def create_category(db:Annotated[AsyncSession, Depends(get_db)], create_cat: CreateCategory):
    await db.execute(insert(Category).values(name=create_cat.name,
                                       parent_id=create_cat.parent_id,
                                       slug=slugify(create_cat.name)))
    await db.commit()
    return {
        'status_code': status.HTTP_201_CREATED,
        'transaction': 'success',
    }

@router.put('/{category_slug}')
async def update_category(db: Annotated[AsyncSession, Depends(get_db)], category_slug: str, update_cat: CreateCategory):
    category = await db.scalar(select(Category).where(Category.slug == category_slug))
    if category is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Category {category_slug} not found",
        )
    category.name = update_cat.name
    # category.description = update_cat.description
    category.slug = slugify(update_cat.name)
    category.parent_id = update_cat.parent_id
    await db.commit()
    return {
        'status_code': status.HTTP_200_OK,
        'transaction': 'success',
    }


@router.delete('/{category_slug}')
async def delete_category(db: Annotated[AsyncSession, Depends(get_db)], category_slug: str):
    category = await db.scalar(select(Category).where(Category.slug == category_slug))
    if category is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Category with slug {category_slug} not found")
    category.is_active = False
    await db.commit()
    return {
        'status_code': status.HTTP_200_OK,
        'transaction': 'success',
    }
