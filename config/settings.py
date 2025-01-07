import json
from dataclasses import dataclass

from environs import Env


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


def load_var(path: str, _class: dataclass):
    env = Env()
    env.read_env()
    attrs = _class.__annotations__
    kwargs = dict()
    for key, value in attrs.items():
        method = getattr(env, value.__name__)
        kwargs[key] = method(key.upper())
    return _class(**kwargs)


db_conf = load_var(path='.env', _class=DBSettings)
pw_conf = load_var(path='.env', _class=PWSettings)
