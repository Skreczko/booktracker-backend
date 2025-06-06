from sqlalchemy import Select, select

from db.model_books import Book


def build_book_list_query(
    *, limit: int, cursor_id: int | None, search: str | None
) -> Select:
    q = select(Book)

    if search:
        pattern = f"%{search}%"
        q = q.where((Book.title.ilike(pattern)) | (Book.author.ilike(pattern)))

    if cursor_id:
        q = q.where(Book.id < cursor_id)

    return q.order_by(Book.id.desc()).limit(limit + 1)
