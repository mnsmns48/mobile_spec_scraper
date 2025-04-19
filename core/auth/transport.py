from fastapi import Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer
from fastapi_users.authentication import BearerTransport
from starlette import status

from config.settings import bearer_token_url

bearer_transport = BearerTransport(tokenUrl=bearer_token_url)


oauth2_scheme = OAuth2PasswordBearer(tokenUrl=bearer_token_url)

async def check_authentication(token: str = Depends(oauth2_scheme)):
    if not token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authorized",
            headers={"WWW-Authenticate": "Bearer"},
        )