import os

import jwt
from fastapi import Header, HTTPException
from jwt import ExpiredSignatureError, InvalidTokenError

EXPECTED_SERVICES = os.getenv("EXPECTED_SERVICES", "")
EXPECTED_SERVICES = [s.strip() for s in EXPECTED_SERVICES.split(",") if s.strip()]


def verify_service_token(authorization: str = Header(...)):
    parts = authorization.split()
    if len(parts) != 2 or parts[0].lower() != "bearer":
        raise HTTPException(401, "Invalid Authorization header")

    token = parts[1]

    try:
        payload = jwt.decode(
            token,
            os.getenv("API_SERVICE_SHARED_SECRET"),
            algorithms=["HS256"]
        )
    except ExpiredSignatureError:
        raise HTTPException(401, "Token expired")
    except InvalidTokenError:
        raise HTTPException(401, "Invalid token")

    service = payload.get("service")

    if service not in EXPECTED_SERVICES:
        raise HTTPException(403, f"Forbidden: wrong service '{service}'")

    return payload
