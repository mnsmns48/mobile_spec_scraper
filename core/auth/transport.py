from fastapi_users.authentication import BearerTransport

from config.settings import api_config

bearer_transport = BearerTransport(tokenUrl=api_config.bearer_token_url)
