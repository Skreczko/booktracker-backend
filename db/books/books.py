from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession
from starlette import status
from starlette.exceptions import HTTPException

from db.books.model_books import Book
from db.books.queries import build_book_list_query
from helpers.queries import print_explain_analyze
from schemas.base import PaginationCursor, PaginatedListResponse
from schemas.books import BookCreateRequest, BookResponse, BookListQueryParams


async def create_book(
    *, request_data: BookCreateRequest, async_db: AsyncSession
) -> None:
    """
    Add a new book to the database using provided data.
    """
    try:
        book = Book(
            title=request_data.title,
            author=request_data.author,
            isbn=request_data.isbn,
            pages=request_data.pages,
            rating=request_data.rating,
        )
        async_db.add(book)
        await async_db.commit()
    except SQLAlchemyError:
        await async_db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create book",
        )


async def get_book_list(
    *, query_params: BookListQueryParams, async_db: AsyncSession
) -> PaginatedListResponse[BookResponse]:
    """
    Return a paginated list of books with optional search and cursor.
    """
    if (
        query_params.search and async_db.bind.dialect.name != "sqlite"
    ):  # sqlite is used for tests
        # Ensure PostgreSQL uses bitmap index scan for trigram searches.
        # For ILIKE operations with trigram indexes on 10M records,
        # we disable sequential scan to guarantee index usage.
        # This provides consistent performance (60ms vs 10s+).
        # LOCAL ensures these settings only apply to this transaction.
        a = 1
        await async_db.execute(text("SET LOCAL enable_seqscan = OFF"))
        await async_db.execute(text("SET LOCAL enable_indexscan = OFF"))

    query = build_book_list_query(
        limit=query_params.limit,
        cursor_id=query_params.cursor_id,
        search=query_params.search,
    )

    # await print_explain_analyze(query, async_db)

    rows = (await async_db.execute(query)).scalars().all()

    has_more = len(rows) == query_params.limit + 1
    items = rows[: query_params.limit]

    next_cursor = (
        PaginationCursor(
            id=items[-1].id,
        )
        if has_more
        else None
    )

    return PaginatedListResponse(
        results=[BookResponse(**item.__dict__) for item in items],
        next_cursor=next_cursor,
    )
