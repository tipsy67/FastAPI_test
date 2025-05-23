from typing import Annotated

from fastapi import APIRouter, HTTPException
from fastapi.params import Depends
from slugify import slugify
from sqlalchemy import insert, select, update
from sqlalchemy.orm import Session
from starlette import status

from app.backend.db_depends import get_db
from app.models import Product, Category
from app.schemas import CreateProduct

router = APIRouter(prefix='/products', tags=['product'])

@router.get('/')
async def get_all_products(db: Annotated[Session, Depends(get_db)]):
    products = db.scalars(select(Product).where(Product.is_active==True, Product.stock > 0)).all()
    return products


@router.post('/', status_code=status.HTTP_201_CREATED)
async def create_product(db: Annotated[Session, Depends(get_db)], create_prod: CreateProduct):
    db.execute(insert(Product).values(
        name=create_prod.name,
        slug=slugify(create_prod.name),
        price=create_prod.price,
        description=create_prod.description,
        is_active=True,
        rating=0.0,
        image_url=create_prod.image_url,
        stock=create_prod.stock,
        category_id=create_prod.category,
    ))
    db.commit()
    return {
        'status_code': status.HTTP_201_CREATED,
        'transaction': 'success',
    }

@router.get('/{category_slug}')
async def get_product_by_cat(db:Annotated[Session, Depends(get_db)], category_slug: str):
    category = db.scalar(select(Category).where(Category.slug == category_slug))
    if category is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Category not found")
    all_categories = [category.id]
    subcategories = [category.id]
    while True:
        subcategories = db.scalars(select(Category.id).where(Category.parent_id.in_(subcategories))).all()
        if len(subcategories) == 0: break
        all_categories.extend(subcategories)

    products = db.scalars(select(Product).where(
        Product.is_active==True, Product.stock>0, Product.category_id.in_(all_categories))).all()

    return products


@router.get('/details/{product_slug}')
async def get_product(db: Annotated[Session, Depends(get_db)], product_slug: str):
    product = db.scalar(select(Product).where(Product.slug == product_slug))
    if product is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f'Product {product_slug} not found'
        )

    return product


@router.put('/{product_slug}')
async def update_product(db: Annotated[Session, Depends(get_db)], product_slug: str, create_prod: CreateProduct):
    product = db.scalar(select(Product).where(Product.slug == product_slug))
    if product is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f'Product {product_slug} not found'
        )

    db.execute(update(Product).where(Product.slug == product_slug).values(
        name=create_prod.name,
        slug=slugify(create_prod.name),
        price=create_prod.price,
        description=create_prod.description,
        is_active=True,
        image_url=create_prod.image_url,
        stock=create_prod.stock,
        category_id=create_prod.category,
    ))
    db.commit()
    return {
        'status_code': status.HTTP_200_OK,
        'transaction': 'success',
    }

@router.delete('/{product_slug}')
async def delete_product(db: Annotated[Session, Depends(get_db)], product_slug: str):
    product = db.scalar(select(Product).where(Product.slug == product_slug))
    if product is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f'Product {product_slug} not found'
        )

    db.execute(update(Product).where(Product.slug == product_slug).values(
        is_active=False,
    ))
    db.commit()
    return {
        'status_code': status.HTTP_200_OK,
        'transaction': 'success',
    }