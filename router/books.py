from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from starlette import status

from db.database import get_async_db
from schemas.base import PaginatedListResponse
from schemas.books import BookCreateRequest, BookResponse, BookListQueryParams
from services.books import service

router = APIRouter(
    prefix="/book",
    tags=["book"],
)


@router.post(
    "/create",
    status_code=status.HTTP_201_CREATED,
    summary="Create a new book entry",
    description="Adds a new book with validated ISBN, page count, and rating (1–5)",
)
async def create_book(
    request_data: BookCreateRequest,
    async_db: AsyncSession = Depends(get_async_db),
) -> None:
    return await service.create_book(request_data=request_data, async_db=async_db)


@router.get(
    "",
    status_code=status.HTTP_200_OK,
    summary="List books with pagination and search",
    description="Books ordered by creation date, with search and cursor pagination",
    response_model=PaginatedListResponse[BookResponse],
)
async def get_book_list(
    query_params: BookListQueryParams = Depends(),
    async_db: AsyncSession = Depends(get_async_db),
) -> PaginatedListResponse[BookResponse]:
    return await service.get_book_list(query_params=query_params, async_db=async_db)
