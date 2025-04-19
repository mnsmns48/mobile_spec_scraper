from fastapi_users.authentication import BearerTransport

from config.settings import bearer_token_url

bearer_transport = BearerTransport(tokenUrl=bearer_token_url)
