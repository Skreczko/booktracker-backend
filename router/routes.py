from fastapi import APIRouter
from router.openapi_swagger import api_router as openapi_swagger_router
from router import books

api_router = APIRouter(prefix="/internal_api")
api_router.include_router(openapi_swagger_router)

api_router.include_router(books.router)
