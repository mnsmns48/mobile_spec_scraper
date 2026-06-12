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
        try:
            response_body = b""
            async for chunk in response.body_iterator:
                response_body += chunk
            async def new_body_iterator():
                yield response_body
            response.body_iterator = new_body_iterator()
            text = response_body.decode("utf-8")
        except Exception as e:
            text = f"<response: unreadable {type(e).__name__}>"
        logger.info(f"Response status: {response.status_code}")
        logger.info(f"Response body: {text}")

        return response
