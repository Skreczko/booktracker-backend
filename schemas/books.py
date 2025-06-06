import datetime
from typing import Annotated

from fastapi.params import Query
from pydantic import Field, field_validator
from stdnum import isbn  # type: ignore

from schemas.base import _BaseModel


class BookListQueryParams(_BaseModel):
    limit: Annotated[
        int,
        Query(20, ge=1, le=500, description="Records to return", examples=[20, 50]),
    ]
    cursor_id: Annotated[
        int | None,
        Query(
            None,
            description="`id` of the last record from the previous page (used as the cursor start).",
            examples=[12978052],
        ),
    ]
    search: Annotated[
        str | None,
        Query(None, description="Filter value applied to both `title` and `author`."),
    ]


class BookBaseModel(_BaseModel):
    title: str = Field(..., description="Book title", min_length=1)
    author: str = Field(..., description="Book author", min_length=1)
    isbn: str = Field(
        ...,
        description="Valid ISBN-10 or ISBN-13 (hyphens/spaces allowed, will be normalized)",
        examples=[
            "978-0-471-11709-4",
            "9780471117094",
            "1-85798-218-5",
            "1857982185",
        ],
    )
    pages: int = Field(..., description="Book total pages", ge=1)
    rating: int = Field(..., description="Book rating", ge=1, le=5)


class BookResponse(BookBaseModel):
    id: int
    created_at: datetime.datetime


class BookCreateRequest(BookBaseModel):
    @field_validator("isbn", mode="after")
    @classmethod
    def validate_isbn(cls, v: str) -> str:
        """
        Validates that the input is a valid ISBN-10 or ISBN-13.

        https://arthurdejong.org/python-stdnum/doc/2.1/stdnum.isbn#module-stdnum.isbn
        """
        return isbn.validate(v)
