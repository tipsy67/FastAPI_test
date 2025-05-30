from typing import Annotated
from fastapi import Depends, HTTPException
from starlette import status

from app.routers.auth import get_current_user


def check_user_permissions(permissions: list[str]):
    async def dependency(get_user: Annotated[dict, Depends(get_current_user)]):
        for permission in permissions:
            if not get_user.get(permission):
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail='Permission denied'
                )
        return get_user
    return dependency