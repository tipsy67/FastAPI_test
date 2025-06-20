from typing import Annotated, Callable
from fastapi import Depends, HTTPException
from starlette import status

from app.models import Product
from app.routers.auth import get_current_user


def check_user_permissions(permissions: list[str]) -> Callable:
    """ Фабрика зависимостей для проверки прав пользователей """
    async def dependency(get_user: Annotated[dict, Depends(get_current_user)]) -> dict:
        for permission in permissions:
            if not get_user.get(permission):
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail='Permission denied'
                )
            else:
                return get_user

    return dependency

async def calculate_rank(product: Product, add: bool, grade: int) -> float:
    """ Подсчет рейтинга продукта при добавлении оценки """
    reviews_count = product.reviews_count or 0
    if add:
        new_rating = (product.rating * reviews_count + grade)/(reviews_count + 1)
    else:
        try:
            new_rating = (product.rating * reviews_count) - grade/(reviews_count - 1)
        except ZeroDivisionError:
            new_rating = 0
    return new_rating