from base64 import urlsafe_b64encode
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives.kdf.argon2 import Argon2id
from os import urandom


def get_random_salt(size: int = 16) -> bytes:
    salt = urandom(size)
    return salt

def get_key(password: bytes, salt: bytes) -> bytes:
    kdf = Argon2id(
        salt=salt,
        length=32,
        iterations=1,
        lanes=4,
        memory_cost=2**21
    )
    key = urlsafe_b64encode(kdf.derive(password))
    return key


def encrypt(key: bytes, data: bytes) -> bytes:
    f = Fernet(key)
    token = f.encrypt(data)
    return token

def decrypt(key: bytes, token: bytes) -> bytes:
    f = Fernet(key)
    data = f.decrypt(token)
    return data