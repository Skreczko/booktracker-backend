import pytest
from sqlalchemy.ext.asyncio import AsyncSession
from starlette import status
from starlette.testclient import TestClient

from conftest import SORTED_BOOKS_COUNT, bulk_create_books, create_fake_book_data
from db.model_books import Book
from schemas.books import BookListQueryParams
from schemas.for_tests import BookTESTBulkCreateUpdateField

pytestmark = pytest.mark.asyncio


class TestBookList:
    async def test_empty_list(self, test_client: TestClient) -> None:
        response = test_client.get("/internal_api/book")
        assert response.status_code == status.HTTP_200_OK

        response_json = response.json()
        assert response_json["results"] == []
        assert response_json["nextCursor"] is None

    async def test_list_with_books_with_sort(
        self, test_client: TestClient, sorted_books: list[Book]
    ) -> None:
        response = test_client.get("/internal_api/book")
        assert response.status_code == status.HTTP_200_OK

        response_json = response.json()
        assert len(response_json["results"]) == min(
            [len(sorted_books), SORTED_BOOKS_COUNT]
        )
        assert response_json["nextCursor"] is None

        for index, book in enumerate(sorted_books):
            assert response_json["results"][index]["id"] == book.id

    @pytest.mark.parametrize(
        "limit,expected_count,has_cursor",
        [
            pytest.param(
                SORTED_BOOKS_COUNT - 1,
                SORTED_BOOKS_COUNT - 1,
                True,
                id="limit < total books",
            ),
            pytest.param(
                SORTED_BOOKS_COUNT,
                SORTED_BOOKS_COUNT,
                False,
                id="limit == total books",
            ),
            pytest.param(
                SORTED_BOOKS_COUNT + 1,
                SORTED_BOOKS_COUNT,
                False,
                id="limit > total books",
            ),
            pytest.param(None, None, None, id="no limit in query_params"),
        ],
    )
    async def test_pagination(
        self,
        test_client: TestClient,
        sorted_books: list[Book],
        limit: int | None,
        expected_count: int | None,
        has_cursor: bool | None,
    ) -> None:
        url = "/internal_api/book"
        if limit:
            url += f"?limit={limit}"
        else:
            limit = BookListQueryParams.model_fields["limit"].default or 20
            expected_count = min([len(sorted_books), limit])
            has_cursor = bool(limit < expected_count)

        response = test_client.get(url)
        assert response.status_code == status.HTTP_200_OK

        response_json = response.json()
        assert len(response_json["results"]) == expected_count

        if has_cursor:
            assert response_json["nextCursor"] is not None
            assert response_json["nextCursor"]["id"] == sorted_books[limit - 1].id
        else:
            assert response_json["nextCursor"] is None

    @pytest.mark.parametrize(
        "limit",
        [
            pytest.param(
                SORTED_BOOKS_COUNT // 2,
            ),
            pytest.param(
                SORTED_BOOKS_COUNT // 3,
            ),
            pytest.param(
                SORTED_BOOKS_COUNT // 4,
            ),
        ],
    )
    async def test_cursor_pagination(
        self, test_client: TestClient, sorted_books: list[Book], limit: int
    ) -> None:
        # Fetch first page
        response = test_client.get(f"/internal_api/book?limit={limit}")
        assert response.status_code == status.HTTP_200_OK

        first_page = response.json()
        assert len(first_page["results"]) == limit
        assert first_page["nextCursor"] is not None

        cursor_id = first_page["nextCursor"]["id"]

        # Fetch second page
        response = test_client.get(
            f"/internal_api/book?limit={limit}&cursorId={cursor_id}"
        )
        assert response.status_code == status.HTTP_200_OK

        second_page = response.json()
        assert len(second_page["results"]) == limit

        for index, book_first_page in enumerate(second_page["results"]):
            assert book_first_page["id"] == sorted_books[limit + index].id

    @pytest.mark.parametrize(
        "exact_search",
        [
            pytest.param(True, id="exact-search-true"),
            pytest.param(False, id="exact-search-false"),
        ],
    )
    @pytest.mark.parametrize(
        "field",
        [
            pytest.param("author", id="search-author"),
            pytest.param("title", id="search-title"),
        ],
    )
    @pytest.mark.parametrize(
        "to_create_count",
        [
            pytest.param(5, id="create-book-5"),
            pytest.param(1, id="create-book-1"),
            pytest.param(0, id="dont-create-book"),
        ],
    )
    async def test_search(
        self,
        async_db_session: AsyncSession,
        test_client: TestClient,
        exact_search: bool,
        sorted_books: list[Book],
        field: str,
        to_create_count: int,
    ) -> None:
        updated_field_value = "dalem-z-siebie-wszystko-cale-30%-piszac-to"
        update_field_list = [
            BookTESTBulkCreateUpdateField(**{field: f"{updated_field_value}-{index}"})
            for index in range(to_create_count)
        ]
        await bulk_create_books(
            async_db_session=async_db_session,
            book_count=to_create_count,
            update_field_list=update_field_list,
        )

        search_value = (
            f"{updated_field_value}-0" if exact_search else updated_field_value
        )

        response = test_client.get(
            f"/internal_api/book?limit=100&search={search_value}"
        )
        assert response.status_code == status.HTTP_200_OK

        data = response.json()

        if to_create_count == 0:
            expected_result = 0
        elif exact_search:
            expected_result = 1
        else:
            expected_result = to_create_count

        assert len(data["results"]) == expected_result

    async def test_search_with_pagination(
        self,
        async_db_session: AsyncSession,
        test_client: TestClient,
        sorted_books: list[Book],
    ) -> None:
        create_count = 2
        updated_field_value = "dalem-z-siebie-wszystko-cale-30%-piszac-to"

        update_field_list = [
            BookTESTBulkCreateUpdateField(**{"title": f"{updated_field_value}-{index}"})
            for index in range(create_count)
        ]
        await bulk_create_books(
            async_db_session=async_db_session,
            book_count=create_count,
            update_field_list=update_field_list,
        )
        response = test_client.get(
            f"/internal_api/book?limit=1&search={updated_field_value}"
        )
        assert response.status_code == status.HTTP_200_OK

        response_json = response.json()

        assert len(response_json["results"]) == 1
        assert response_json["nextCursor"] is not None
        assert updated_field_value in response_json["results"][0]["title"]


class TestCreateBook:
    @pytest.mark.parametrize(
        "isbn",
        [
            pytest.param(
                "9788375780635",
                id="ISBN-13",
            ),
            pytest.param(
                "978-8375780635",
                id="ISBN-13",
            ),
            pytest.param(
                "8375780634",
                id="ISBN-10",
            ),
        ],
    )
    async def test_create_book_success(
        self, test_client: TestClient, isbn: str
    ) -> None:
        response = test_client.post(
            "/internal_api/book/create",
            json={
                **create_fake_book_data(),
                "isbn": isbn,
            },
        )
        assert response.status_code == status.HTTP_201_CREATED

    @pytest.mark.parametrize(
        "field,value",
        [
            ("title", ""),
            ("author", ""),
            ("isbn", "invalid-isbn"),
            ("isbn", ""),
            ("pages", 0),
            ("rating", 6),
        ],
    )
    async def test_create_book_validation(
        self, test_client: TestClient, field: str, value: str | int
    ) -> None:
        response = test_client.post(
            "/internal_api/book/create", json={**create_fake_book_data(), field: value}
        )
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
