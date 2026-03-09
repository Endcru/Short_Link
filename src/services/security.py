from datetime import datetime, timedelta, timezone
from jose import jwt
from passlib.context import CryptContext

KEY = "qwerty12345"
ALG = "HS256"

crypt_context = CryptContext(schemes=["argon2"], deprecated="auto")

def hash_password(password: str) -> str:
    return crypt_context.hash(password)

def check_password(password: str, hashed: str) -> bool:
    return crypt_context.verify(password, hashed)

def create_access_token(data: dict)-> str:
    expire = datetime.now(timezone.utc) + timedelta(hours=5)
    encode_data = data.copy()
    encode_data.update({"exp": expire})
    return jwt.encode(encode_data, KEY, algorithm=ALG)