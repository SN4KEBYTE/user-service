from datetime import datetime, timedelta
from typing import Optional

from jose import jwt

from app import models

SECRET_KEY = "09d25e094faa6ca2556c818166b7a9563b93f7099f6f0f4caa6cf63b88e8d3e7"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60


def create_access_token(data: dict,
                        expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    expire = datetime.utcnow() + (expires_delta if expires_delta else timedelta(minutes=15))

    to_encode.update({"exp": expire})

    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)


def verify_password(pwd_context,
                    plain_password,
                    hashed_password):
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(pwd_context,
                      password):
    return pwd_context.hash(password)


def authenticate_user(pwd_context,
                      db,
                      username,
                      password):
    user = db.query(models.User).filter(models.User.login == username).first()

    if not user:
        return False

    if not verify_password(pwd_context,
                           password,
                           user.password):
        return False

    return user
