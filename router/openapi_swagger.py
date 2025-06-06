from typing import Any

from fastapi import APIRouter, Depends
from fastapi.openapi.docs import get_swagger_ui_html
from starlette.requests import Request
from starlette.responses import HTMLResponse

from db.openapi import get_access_to_swagger

api_router = APIRouter()


@api_router.get("/docs", include_in_schema=False)
async def get_custom_swagger_ui_html(
    username: str = Depends(get_access_to_swagger),  # type: ignore
) -> HTMLResponse:
    return get_swagger_ui_html(
        openapi_url="/internal_api/openapi.json", title="Customized docs"
    )


@api_router.get("/openapi.json", include_in_schema=False)
async def openapi(
    request: Request, username: str = Depends(get_access_to_swagger)
) -> dict[str, Any]:  # type: ignore
    return request.app.openapi()
