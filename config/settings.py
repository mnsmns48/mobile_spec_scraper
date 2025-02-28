import json
import os
from dataclasses import dataclass
from pathlib import Path

from environs import Env

root_path = Path(os.path.abspath(__file__)).parent.parent


@dataclass
class DBSettings:
    db_username: str
    db_password: str
    db_host: str
    db_port: int
    database: str


@dataclass
class PWSettings:
    headless_mode: bool
    enable_proxy: bool
    proxy_timeout: int


@dataclass
class AppSetup:
    app_port: int


def load_var(_class: dataclass):
    env = Env()
    env.read_env(path=f'{root_path}/setup/.env')
    attrs = _class.__annotations__
    kwargs = dict()
    for key, value in attrs.items():
        method = getattr(env, value.__name__)
        kwargs[key] = method(key.upper())
    return _class(**kwargs)


db_conf = load_var(_class=DBSettings)
pw_conf = load_var(_class=PWSettings)
app_setup = load_var(_class=AppSetup)
