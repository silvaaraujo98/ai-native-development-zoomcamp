from fastapi import Depends

from ..auth import AuthPrincipal, auth_error, require_bearer
from ..store import api_error, store


def current_principal(token: str = Depends(require_bearer)) -> AuthPrincipal:
    principal = store.principal_for_token(token)
    if not principal:
        raise auth_error()
    return principal


def current_user(principal: AuthPrincipal = Depends(current_principal)) -> AuthPrincipal:
    if principal.kind != "user":
        raise api_error(403, "forbidden", "An authenticated interviewer token is required.")
    return principal


def session_reader(session_id: str, principal: AuthPrincipal = Depends(current_principal)) -> AuthPrincipal:
    if not store.can_access_session(principal, session_id):
        raise api_error(403, "forbidden", "You cannot access this session.")
    return principal


def session_editor(session_id: str, principal: AuthPrincipal = Depends(current_principal)) -> AuthPrincipal:
    if not store.can_edit_session(principal, session_id):
        raise api_error(403, "forbidden", "You cannot edit this session.")
    return principal
