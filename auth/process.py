import jwt

from config.settings import auth_conf


def encode_jwt(payload: dict,
               key: str = auth_conf.private_key_path.read_text(),
               algorithm: str = auth_conf.algorithm):
    encoded = jwt.encode(payload, key, algorithm)
    return encoded


def decode_jwt(token: str | bytes,
               public_key: str = auth_conf.public_key_path.read_text(),
               algorithm: str = auth_conf.algorithm):
    decoded = jwt.decode(token, public_key, algorithms=[algorithm])
    return decoded
