import random
from typing import Any

import pytest
import pytest_asyncio
from faker import Faker
from fastapi.testclient import TestClient
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy.pool import StaticPool

from db.model_books import Book
from db.database import Base, get_async_db
from main import app
from schemas.books import BookCreateRequest
from schemas.for_tests import BookTESTBulkCreateUpdateField

TEST_DATABASE_URL = "sqlite+aiosqlite:///:memory:"

test_async_engine = create_async_engine(
    TEST_DATABASE_URL,
    poolclass=StaticPool,
    connect_args={"check_same_thread": False},
)

TestAsyncSessionLocal = async_sessionmaker(
    bind=test_async_engine,
    class_=AsyncSession,
    expire_on_commit=False,
)

fake = Faker()

SORTED_BOOKS_COUNT = 20


@pytest_asyncio.fixture
async def async_db_session() -> AsyncSession:
    """Fixture providing test database session."""
    async with test_async_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    async with TestAsyncSessionLocal() as session:
        yield session

    async with test_async_engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)


@pytest.fixture
def test_client(async_db_session: AsyncSession) -> TestClient:
    """Fixture providing test client with overridden database dependency."""

    async def override_get_async_db():
        yield async_db_session

    app.dependency_overrides[get_async_db] = override_get_async_db  # type: ignore

    with TestClient(app) as client:
        yield client

    app.dependency_overrides.clear()  # type: ignore


def create_fake_book_data() -> dict[str, Any]:
    return BookCreateRequest(
        **{
            "title": fake.sentence(nb_words=random.randint(1, 5)).rstrip("."),
            "author": fake.name(),
            "isbn": fake.isbn13(separator="-"),
            "pages": random.randint(100, 1000),
            "rating": random.randint(1, 5),
        }
    ).model_dump(mode="json")


async def bulk_create_books(
    *,
    async_db_session: AsyncSession,
    book_count: int = SORTED_BOOKS_COUNT,
    update_field_list: list[BookTESTBulkCreateUpdateField] | None = None,
) -> list[Book]:
    """
    Create multiple books in the database for testing purposes.

    Args:
        async_db_session: Database session for async operations
        book_count: Number of books to create (default: 20)
        update_field_list: Optional list of field overrides for each book.
                          If provided, must contain exactly `book_count` items.
                          Each item can override specific fields (title, author, etc.)
                          for the corresponding book at that index.

    Example:
        # Create 3 books with specific titles:
        update_fields = [
            BookTESTBulkCreateUpdateField(title="Python Guide"),
            BookTESTBulkCreateUpdateField(title="FastAPI Tutorial"),
            BookTESTBulkCreateUpdateField(author="John Doe", rating=5)
        ]
        books = await bulk_create_books(
            async_db_session=session,
            book_count=3,
            update_field_list=update_fields
        )

    Returns:
        list[Book]: Created books sorted by ID in descending order (newest first).
    """
    if update_field_list:
        assert len(update_field_list) == book_count

    books = []
    for index in range(book_count):
        book_data = create_fake_book_data()

        if update_field_list:
            # Override specific fields for this book if provided
            update_data = update_field_list[index].model_dump(
                mode="json", exclude_unset=True
            )
            book_data.update(update_data)

        book = Book(**book_data)
        async_db_session.add(book)
        books.append(book)

    await async_db_session.commit()

    for book in books:
        await async_db_session.refresh(book)

    return sorted(books, key=lambda book: book.id, reverse=True)


@pytest_asyncio.fixture
async def sorted_books(async_db_session: AsyncSession) -> list[Book]:
    """Fixture creating multiple books for pagination tests, sorted by id descending. Sorting is crucial."""
    return await bulk_create_books(async_db_session=async_db_session)
