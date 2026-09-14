from fastapi import APIRouter, HTTPException, status

from app.auth import create_access_token, get_current_user, verify_password
from app.models import LoginRequest, LoginResponse, UserPublic
from app.store import store
from fastapi import Depends
from app.models import UserRecord


router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/login", response_model=LoginResponse)
def login(payload: LoginRequest) -> LoginResponse:
    user = store.get_user_by_username(payload.username)
    if user is None or not verify_password(payload.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid username or password.",
        )
    token = create_access_token()
    store.save_token(token, user.id)
    return LoginResponse(access_token=token, user=UserPublic(id=user.id, name=user.name))


@router.get("/me", response_model=UserPublic)
def me(user: UserRecord = Depends(get_current_user)) -> UserPublic:
    return UserPublic(id=user.id, name=user.name)
