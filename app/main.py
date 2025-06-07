from fastapi import FastAPI

from app.routers import category, product, auth, permission, review

app = FastAPI()
@app.get('/')
async def root() -> dict:
    return {'message': 'My app'}

app.include_router(category.router)
app.include_router(product.router)
app.include_router(auth.router)
app.include_router(permission.router)
app.include_router(review.router)