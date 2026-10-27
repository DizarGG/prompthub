from datetime import datetime, timedelta, timezone
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from jose import JWTError, jwt
from pwdlib import PasswordHash
from sqlalchemy.orm import Session
from app.config import jwt_secret
from app.datasourse.db_users import get_db
from app.datasourse.models import User

JWT_router = APIRouter(tags=['Авторизация'])
oauth2_scheme = OAuth2PasswordBearer(tokenUrl='/login')
password_hash = PasswordHash.recommended()
ALGORITHM = 'HS256'
ACCESS_TOKEN_EXPIRE_MINUTES = 30


def get_secret():
    return jwt_secret()


def hash_password(password: str) -> str:
    return password_hash.hash(password)


def verify_password(password: str, hashed: str) -> bool:
    return password_hash.verify(password, hashed)


def create_access_token(data: dict):
    payload = data.copy()
    payload['exp'] = datetime.now(timezone.utc) + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    return jwt.encode(payload, get_secret(), algorithm=ALGORITHM)


def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)) -> User:
    invalid = HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                            detail='Invalid authentication credentials',
                            headers={'WWW-Authenticate': 'Bearer'})
    try:
        payload = jwt.decode(token, get_secret(), algorithms=[ALGORITHM])
        user_id = int(payload['sub'])
    except (JWTError, KeyError, TypeError, ValueError):
        raise invalid
    user = db.get(User, user_id)
    if user is None or not user.is_active:
        raise invalid
    return user


@JWT_router.post('/login')
def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = db.query(User).filter(User.username == form_data.username).first()
    if user is None or not user.is_active or not verify_password(form_data.password, user.password):
        raise HTTPException(status_code=401, detail='Incorrect username or password')
    return {'access_token': create_access_token({'sub': str(user.id)}), 'token_type': 'bearer'}
