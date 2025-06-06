from sqlalchemy import CheckConstraint, Index, String, Integer
from sqlalchemy.orm import Mapped, mapped_column

from db.model_base import _BaseCreated


class Book(_BaseCreated):
    __tablename__ = "books"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    title: Mapped[str] = mapped_column(String, nullable=False)
    author: Mapped[str] = mapped_column(String, nullable=False)
    isbn: Mapped[str] = mapped_column(String, nullable=False)
    pages: Mapped[int] = mapped_column(Integer, nullable=False)
    rating: Mapped[int] = mapped_column(Integer, nullable=False)

    __table_args__ = (
        Index(
            "idx_title_trgm",
            "title",
            postgresql_using="gin",
            postgresql_ops={"title": "gin_trgm_ops"},
        ),
        Index(
            "idx_author_trgm",
            "author",
            postgresql_using="gin",
            postgresql_ops={"author": "gin_trgm_ops"},
        ),
        CheckConstraint("rating >= 1 AND rating <= 5", name="check_rating_range"),
    )

    def __init__(
        self,
        title: str,
        author: str,
        isbn: str,
        pages: int,
        rating: int,
    ):
        self.title = title
        self.author = author
        self.isbn = isbn
        self.pages = pages
        self.rating = rating

    def __repr__(self) -> str:
        return f"Book {self.id} {self.created_at}"
