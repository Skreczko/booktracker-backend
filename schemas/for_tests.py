from pydantic import BaseModel


class BookTESTBulkCreateUpdateField(BaseModel):
    """
    ONLY FOR TESTING PURPOSES
    """

    title: str | None = None
    author: str | None = None
