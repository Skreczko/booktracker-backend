from fastapi import FastAPI
from fastapi.exceptions import RequestValidationError
from pydantic import ValidationError
from fastapi import Request
from fastapi.middleware.cors import CORSMiddleware
from router.routes import api_router
from settings import get_config

config = get_config()

app = FastAPI(
    docs_url="/docs",
    openapi_url="/openapi.json",
    redoc_url=None,
    title="book tracker backend",
    version="1.0.0",
    openapi_version="1.0.0",
    contact={
        "email": "dawid.skreczko@gmail.com",
    },
    license_info={
        "name": "Powered with ❤️ ",
    },
    debug=config.debug,
    extra={"requests_client": None},
)

app.include_router(api_router)


@app.exception_handler(ValidationError)
async def validation_exception_handler(request: Request, e: ValidationError) -> None:
    """
    Custom exception handler for Pydantic ValidationError.

    This handler converts a Pydantic ValidationError into a FastAPI RequestValidationError,
    ensuring that FastAPI returns a structured validation error response.

    Parameters:
    - request (Request): The incoming HTTP request object.
    - e (ValidationError): The original validation error captured by Pydantic.

    Raises:
    - RequestValidationError: Re-raises the error as a FastAPI validation error,
      enabling FastAPI to return a standard error response with the validation details.
    """
    raise RequestValidationError(errors=e.errors())


LOCAL_ROUTER_DOMAINS = [
    "localhost:3000",
    "http://localhost:3000",
]

origins = []

origins.extend(LOCAL_ROUTER_DOMAINS)


app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
