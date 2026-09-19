from fastapi import APIRouter

from ..models import LoginRequest, TokenResponse
from ..store import api_error, store


router = APIRouter(prefix="/auth", tags=["Auth"])


@router.post("/login", response_model=TokenResponse)
def login(request: LoginRequest) -> TokenResponse:
    token = store.authenticate_user(request.email, request.password)
    if not token:
        raise api_error(401, "unauthorized", "Invalid email or password.")
    return TokenResponse(accessToken=token)
