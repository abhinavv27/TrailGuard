from sqlalchemy.orm import Session

from app.core.security import hash_password, verify_password
from app.models.user import User
from app.schemas.auth import UserResponse


class AuthService:

    @staticmethod
    def authenticate_user(email: str, password: str, db: Session) -> User | None:
        user = db.query(User).filter(User.email == email).first()
        if not user:
            return None
        if not verify_password(password, user.hashed_password):
            return None
        return user

    @staticmethod
    def create_user(email: str, password: str, display_name: str, db: Session) -> User:
        user = User(
            email=email,
            hashed_password=hash_password(password),
            display_name=display_name,
            role="analyst",
        )
        db.add(user)
        db.commit()
        db.refresh(user)
        return user

    @staticmethod
    def get_user_by_id(user_id: str, db: Session) -> User | None:
        return db.query(User).filter(User.id == user_id).first()

    @staticmethod
    def user_to_response(user: User) -> UserResponse:
        return UserResponse(
            id=str(user.id),
            email=user.email,
            display_name=user.display_name,
            role=user.role,
            is_active=user.is_active,
        )
