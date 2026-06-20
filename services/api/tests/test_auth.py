"""Tests for authentication endpoints."""
from app.core.security import create_access_token, hash_password, verify_password


def test_hash_password():
    hashed = hash_password("test1234")
    assert hashed != "test1234"
    assert verify_password("test1234", hashed)
    assert not verify_password("wrong", hashed)

def test_create_token():
    data = {"sub": "user-1", "role": "analyst"}
    token = create_access_token(data)
    assert token is not None
    assert isinstance(token, str)

def test_login_success(db_session, demo_user):
    from app.services.auth_service import AuthService
    user = AuthService.authenticate_user("test@trailguard.ai", "test1234", db_session)
    assert user is not None
    assert user.email == "test@trailguard.ai"

def test_login_invalid_password(db_session, demo_user):
    from app.services.auth_service import AuthService
    user = AuthService.authenticate_user("test@trailguard.ai", "wrong", db_session)
    assert user is None

def test_login_nonexistent_user(db_session):
    from app.services.auth_service import AuthService
    user = AuthService.authenticate_user("nonexistent@test.com", "test1234", db_session)
    assert user is None

def test_get_user_by_id(db_session, demo_user):
    from app.services.auth_service import AuthService
    user = AuthService.get_user_by_id(demo_user.id, db_session)
    assert user is not None
    assert user.id == demo_user.id
