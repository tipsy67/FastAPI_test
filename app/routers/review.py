from datetime import datetime
from typing import Annotated

from fastapi import APIRouter, HTTPException
from fastapi.params import Depends
from sqlalchemy import select, insert
from sqlalchemy.ext.asyncio import AsyncSession
from starlette import status

from app.backend.db_depends import get_db
from app.models import Product
from app.models.review import Review
from app.routers.auth import get_current_user
from app.routers.services import check_user_permissions, calculate_rank
from app.schemas import CreateReview

router = APIRouter(prefix='/reviews', tags=['review'])

@router.get('/')
async def get_all_reviews(db: Annotated[AsyncSession,Depends(get_db)],
                          get_user: Annotated[dict, Depends(get_current_user)]):
    reviews = await db.scalars(select(Review).where(Review.is_active == True))
    return reviews.all()

@router.get('/{product_slug}')
async def get_reviews_by_product(db: Annotated[AsyncSession, Depends(get_db)],
                                 get_user: Annotated[dict, Depends(get_current_user)],
                                 product_slug: str):
    product = await db.scalar(select(Product).where(Product.slug == product_slug))
    if product is None:
        raise HTTPException(status_code=404, detail='Product not found')
    reviews = await db.scalars(select(Review).where(Review.product_id == product.id, Review.is_active == True))
    return reviews.all()

@router.post('/', status_code=status.HTTP_201_CREATED)
async def create_review(db: Annotated[AsyncSession, Depends(get_db)],
                        get_user: Annotated[dict, Depends(check_user_permissions(['is_supplier']))],
                        new_review: CreateReview):
    product = await db.scalar(select(Product).where(Product.id == new_review.product_id))
    if product is None:
        raise HTTPException(status_code=404, detail='Product not found')
    await db.execute(insert(Review).values(
        user_id = get_user.get('id'),
        product_id = new_review.product_id,
        comment = new_review.comment,
        comment_date = datetime.now(),
        grade = new_review.grade,
    ))

    product.rating = await calculate_rank(product, True, new_review.grade)
    product.reviews_count += 1

    await db.commit()

    return new_review

@router.delete('/{review_id}')
async def delete_review(db: Annotated[AsyncSession, Depends(get_db)],
                        get_user: Annotated[dict, Depends(check_user_permissions(['is_admin']))],
                        review_id: int):
    review = await db.scalar(select(Review).where(Review.id == review_id))
    if review is None:
        raise HTTPException(status_code=404, detail='Review not found')

    product = await db.scalar(select(Product).where(Product.id == review.product_id))
    if product is None:
        raise HTTPException(status_code=404, detail='Product not found')

    product.rating = await calculate_rank(product, not review.is_active, review.grade)

    if review.is_active:
        review.is_active = False
        message=''
        product.reviews_count -= 1
    else:
        review.is_active = True
        message='un'
        product.reviews_count += 1


    await db.commit()

    return {
        'status_code': status.HTTP_200_OK,
        'message': f'Review {message}deleted',
    }