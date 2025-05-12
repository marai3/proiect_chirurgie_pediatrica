from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from datetime import datetime, timedelta
from typing import Optional

SECRET_KEY = "secrettoken2025"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

fake_users_db = {
    "medic": {
        "username": "medic",
        "hashed_password": "$2b$12$7u4yY6HPiOBKsPK3l3F2JO4c9bSOYSFzoDdxiQTKvR1GgOLJYs8te",  # parola: medic123
        "role": "doctor"
    },
    "asistent": {
        "username": "asistent",
        "hashed_password": "$2b$12$JwwGFbZeHUcvFD..nKf7RuIIo89H4gJ4ZiTCUhAn5QPPkFFJ/z30y",  # parola: asistent123
        "role": "nurse"
    },
    "cercetator": {
        "username": "cercetator",
        "hashed_password": "$2b$12$Ovcu.stuJ4l1mSV7MWTsH.2EX6F1aCQq0oeAnGu9QOEuqU7MWNfxi",  # parola: research123
        "role": "researcher"
    }
}

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    expire = datetime.utcnow() + (expires_delta or timedelta(minutes=30))
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

def get_current_user(token: str = Depends(oauth2_scheme)):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username = payload.get("sub")
        role = payload.get("role")
        if username is None or role is None:
            raise HTTPException(status_code=401, detail="Invalid token")
        return {"username": username, "role": role}
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid token")

def role_required(required_roles: list):
    def verifier(user=Depends(get_current_user)):
        if user["role"] not in required_roles:
            raise HTTPException(status_code=403, detail="Access denied.")
        return user
    return verifier