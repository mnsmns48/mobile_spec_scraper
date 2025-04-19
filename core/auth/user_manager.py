import logging
from typing import Optional, TYPE_CHECKING

from fastapi_users import IntegerIDMixin, BaseUserManager

from config.settings import var_types, access_token_cfg
from database.models import User

if TYPE_CHECKING:
    from fastapi import Request

log = logging.getLogger(__name__)


class UserManager(IntegerIDMixin, BaseUserManager[User, var_types.UserIdType]):
    reset_password_token_secret = access_token_cfg.reset_password_token_secret
    verification_token_secret = access_token_cfg.verification_token_secret

    async def on_after_register(self, user: User, request: Optional["Request"] = None):
        log.warning("User %r has registered.", user.id)
        # await send_new_user_notification(user)

    async def on_after_request_verify(self, user: User, token: str, request: Optional["Request"] = None):
        log.warning("Verification requested for user %r. Verification token: %r", user.id, token)

    async def on_after_forgot_password(self, user: User, token: str, request: Optional["Request"] = None):
        log.warning("User %r has forgot their password. Reset token: %r", user.id, token)
