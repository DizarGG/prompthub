from typing import Annotated
from fastapi import Depends, FastAPI, HTTPException, status,APIRouter
from fastapi.security import HTTPBasic, HTTPBasicCredentials
import secrets

security = HTTPBasic()
Basic_router = APIRouter()


def get_current_user(credentials:  Annotated[HTTPBasicCredentials, Depends(security)]):

    current_username_bytes = credentials.username.encode("utf8")
    correct_username_bytes = b"stanleyjobson"
    correct_username = secrets.compare_digest(
        current_username_bytes, correct_username_bytes
    )
    current_password_bytes = credentials.password.encode("utf8")
    correct_password_bytes = b"swordfish"
    correct_password = secrets.compare_digest(
        current_password_bytes, correct_password_bytes
    )

    if not (correct_username and correct_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Basic"},
        )

    return credentials.username

@Basic_router.get("/profile")
def profile(user: str = Depends(get_current_user)):
    return {
        "message": f"Hello {user}"
    }