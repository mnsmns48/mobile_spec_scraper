from fastapi_users import FastAPIUsers

from api.dependencies.backend import authentication_backend
from api.dependencies.user_manager import get_user_manager
from config.settings import var_types
from database.models import User

fastapi_users = FastAPIUsers[User, var_types.UserIdType](get_user_manager, [authentication_backend])
