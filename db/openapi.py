from fastapi import Security
from fastapi.security import HTTPBasic, HTTPBasicCredentials
from starlette import status
from starlette.exceptions import HTTPException

from settings import get_config

config = get_config()
security = HTTPBasic()


def get_access_to_swagger(
    credentials: HTTPBasicCredentials = Security(security),
) -> str:
    correct_username = config.swagger_username
    correct_password = config.swagger_password
    if (
        credentials.username == correct_username.get_secret_value()
        and credentials.password == correct_password.get_secret_value()
    ):
        return credentials.username
    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        headers={"WWW-Authenticate": "Basic"},
    )
