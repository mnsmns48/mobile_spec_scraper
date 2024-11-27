from dataclasses import dataclass

from environs import Env


@dataclass
class DBSettings:
    db_username: str
    db_password: str
    db_host: str
    db_port: int
    database: str


def load_var(path: str):
    env = Env()
    env.read_env()

    return DBSettings(db_username=env.str("DB_USERNAME"),
                      db_password=env.str("DB_PASSWORD"),
                      db_host=env.str("DB_HOST"),
                      db_port=env.int("DB_PORT"),
                      database=env.str("DATABASE")
                      )


db_settings = load_var(path='.env')
