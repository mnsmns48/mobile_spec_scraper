from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request, ClientDisconnect

from config import logger


class RequestLoggingMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        method = request.method
        url = request.url.path
        client = request.client.host if request.client else "unknown"
        try:
            raw_body = await request.body()
            body_text = raw_body.decode("utf-8") if raw_body else ""
        except UnicodeDecodeError:
            body_text = "<body: cannot decode utf-8>"
        except ClientDisconnect:
            body_text = "<body: client disconnected>"
        except Exception as e:
            body_text = f"<body: unexpected error {type(e).__name__}>"
        logger.info(f"Incoming request: {method} {url} from {client}")
        if body_text:
            logger.info(f"Body: {body_text}")
        response = await call_next(request)
        logger.info(f"Response status: {response.status_code}")

        return response
