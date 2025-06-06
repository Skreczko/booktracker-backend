from typing import Generic, TypeVar

from pydantic import BaseModel, Field
from pydantic.alias_generators import to_camel

T = TypeVar("T")


class _BaseModel(BaseModel):
    class Config:
        alias_generator = to_camel
        from_attributes = True
        populate_by_name = True


class PaginationCursor(_BaseModel):
    id: int = Field(
        ...,
        description="`id` of the last record from the previous page (used as the cursor start).",
        examples=[12978052],
    )


class PaginatedListResponse(_BaseModel, Generic[T]):
    results: list[T]
    next_cursor: PaginationCursor | None

    class Config(_BaseModel.Config):
        arbitrary_types_allowed = True
