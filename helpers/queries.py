from typing import TypeVar

from sqlalchemy import Select, text
from sqlalchemy.ext.asyncio import AsyncSession

T = TypeVar("T")


async def print_explain_analyze(query: Select, async_db: AsyncSession) -> None:
    """
    Prints the query execution plan with analysis data for a given SQLAlchemy Select statement.

    This function runs an `EXPLAIN (ANALYZE, BUFFERS, FORMAT TEXT)` query on the provided SQLAlchemy statement,
    allowing you to inspect how PostgreSQL (or another compatible database) executes the statement, including
    performance metrics and buffer usage.
    """
    explain_stmt = text(
        f"EXPLAIN (ANALYZE, BUFFERS, FORMAT TEXT) {query.compile(compile_kwargs={'literal_binds': True})}"
    )
    explain_result = await async_db.execute(explain_stmt)
    print("Plan:")
    for row in explain_result:
        print(row[0])
