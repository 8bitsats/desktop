from datetime import datetime, timedelta
from typing import Dict, Optional

import jwt
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jwt.exceptions import DecodeError, ExpiredSignatureError
from pydantic import ValidationError

from src.config import settings
from src.models.session import Session
from src.models.user import User
from .database import MongoDB

# OAuth2 scheme for token authentication
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/auth/login")

# Function to create JWT token
def create_jwt_token(user_id: str) -> str:
    expire = datetime.utcnow() + timedelta(seconds=settings.JWT_EXPIRATION)
    payload = {"sub": user_id, "exp": expire}
    token = jwt.encode(payload, settings.JWT_SECRET, algorithm="HS256")
    return token

# Function to get current user from token
async def get_current_user(token: str = Depends(oauth2_scheme)) -> User:
    try:
        payload = jwt.decode(token, settings.JWT_SECRET, algorithms=["HS256"])
        user_id: str = payload.get("sub")
        if user_id is None:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")
        user_doc = await MongoDB.db.users.find_one({"_id": user_id})
        if not user_doc:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="User not found")
        return User(**user_doc)
    except (DecodeError, ExpiredSignatureError, ValidationError):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid or expired token") 