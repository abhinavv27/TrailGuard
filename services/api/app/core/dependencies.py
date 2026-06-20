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


ROLE_HIERARCHY = {
    "analyst": 1,
    "investigator": 2,
    "admin": 3,
}


def require_role(required_role: str):
    def role_checker(current_user: dict = Depends(get_current_user)):
        user_role = current_user.get("role", "")
        user_level = ROLE_HIERARCHY.get(user_role, 0)
        required_level = ROLE_HIERARCHY.get(required_role, 0)
        if user_level < required_level:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Role '{required_role}' or higher is required (current: {user_role})",
            )
        return current_user

    return role_checker
