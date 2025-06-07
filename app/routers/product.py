from typing import Annotated

from fastapi import APIRouter, HTTPException
from fastapi.params import Depends
from slugify import slugify
from sqlalchemy import insert, select, update
from sqlalchemy.ext.asyncio import AsyncSession

from starlette import status

from app.backend.db_depends import get_db
from app.models import Product, Category
from app.routers.auth import get_current_user
from app.routers.services import check_user_permissions
from app.schemas import CreateProduct

router = APIRouter(prefix='/products', tags=['product'])

@router.get('/')
async def get_all_products(db: Annotated[AsyncSession, Depends(get_db)],
                           get_user: Annotated[dict, Depends(get_current_user)]):
    products = await db.scalars(select(Product).where(Product.is_active==True, Product.stock > 0))
    return products.all()


@router.post('/', status_code=status.HTTP_201_CREATED)
async def create_product(db: Annotated[AsyncSession, Depends(get_db)],
                          get_user: Annotated[dict, Depends(check_user_permissions(['is_admin', 'is_supplier']))],
                          create_prod: CreateProduct):
    category = await db.scalar(select(Category).where(Category.id == create_prod.category_id))
    if category is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail='There is no category found'
        )
    await db.execute(insert(Product).values(
        name=create_prod.name,
        slug=slugify(create_prod.name),
        price=create_prod.price,
        description=create_prod.description,
        is_active=True,
        rating=0.0,
        image_url=create_prod.image_url,
        stock=create_prod.stock,
        category_id=create_prod.category_id,
        supplier_id=get_user.get('id'),
    ))
    await db.commit()
    return {
        'status_code': status.HTTP_201_CREATED,
        'transaction': 'success',
    }

@router.get('/{category_slug}')
async def get_product_by_cat(db:Annotated[AsyncSession, Depends(get_db)],
                            get_user: Annotated[dict, Depends(get_current_user)],
                            category_slug: str):
    category = await db.scalar(select(Category).where(Category.slug == category_slug))
    if category is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Category not found")
    all_categories = [category.id]
    subcategories = [category.id]
    while True:
        subcategories = await db.scalars(select(Category.id).where(Category.parent_id.in_(subcategories)))
        subcategories = subcategories.all()
        if len(subcategories) == 0: break
        all_categories.extend(subcategories)

    products = await db.scalars(select(Product).where(
        Product.is_active==True, Product.stock>0, Product.category_id.in_(all_categories)))

    return products.all()


@router.get('/details/{product_slug}')
async def get_product(db: Annotated[AsyncSession, Depends(get_db)],
                        get_user: Annotated[dict, Depends(get_current_user)], product_slug: str):
    product = await db.scalar(select(Product).where(Product.slug == product_slug))
    if product is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f'Product {product_slug} not found'
        )

    return product


@router.put('/{product_slug}')
async def update_product(db: Annotated[AsyncSession, Depends(get_db)],
                         get_user: Annotated[dict, Depends(check_user_permissions(['is_admin', 'is_supplier']))],
                         product_slug: str, create_prod: CreateProduct):
    product = await db.scalar(select(Product).where(Product.slug == product_slug))
    if product is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f'Product {product_slug} not found'
        )
    if product.id != get_user.get('id') and not get_user.get('is_admin'):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail='Permission denied'
        )
    category = await db.scalar(select(Category).where(Category.id == create_prod.category))
    if category is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail='There is no category found'
        )
    product.name = create_prod.name
    product.description = create_prod.description
    product.slug = slugify(create_prod.name)
    product.is_active = True
    product.rating = create_prod.rating
    product.image_url = create_prod.image_url
    product.stock = create_prod.stock
    product.category_id = create_prod.category

    await db.commit()
    return {
        'status_code': status.HTTP_200_OK,
        'transaction': 'success',
    }

@router.delete('/{product_slug}')
async def delete_product(db: Annotated[AsyncSession, Depends(get_db)],
                         get_user: Annotated[dict, Depends(check_user_permissions(['is_admin', 'is_supplier']))],
                         product_slug: str):
    product = await db.scalar(select(Product).where(Product.slug == product_slug))
    if product is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f'Product {product_slug} not found'
        )

    if product.id != get_user.get('id') and not get_user.get('is_admin'):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail='Permission denied'
        )

    product.is_active = False

    await db.commit()
    return {
        'status_code': status.HTTP_200_OK,
        'transaction': 'success',
    }