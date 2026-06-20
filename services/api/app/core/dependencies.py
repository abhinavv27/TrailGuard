from fastapi import Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.security import get_current_user
from app.db.session import get_db as _get_db


def get_db():
    _db = _get_db()
    try:
        yield _db
    finally:
        _db.close()


def require_role(role: str):
    def role_checker(current_user: dict = Depends(get_current_user)):
        user_role = current_user.get("role", "")
        if user_role != role:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Role '{role}' is required",
            )
        return current_user

    return role_checker
