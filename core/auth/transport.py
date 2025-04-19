from fastapi import Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer
from fastapi_users.authentication import BearerTransport, CookieTransport
from starlette import status

from config.settings import bearer_token_url, access_token_cfg

bearer_transport = BearerTransport(tokenUrl=bearer_token_url)
cookie_transport = CookieTransport(cookie_name="access_token", cookie_max_age=access_token_cfg.lifetime_seconds)

oauth2_scheme = OAuth2PasswordBearer(tokenUrl=bearer_token_url)


async def check_authentication(token: str = Depends(oauth2_scheme)):
    if not token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authorized",
            headers={"WWW-Authenticate": "Bearer"},
        )
