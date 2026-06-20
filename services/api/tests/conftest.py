"""Test configuration and fixtures."""
import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.core.security import hash_password
from app.db.session import Base
from app.models.user import User

TEST_DATABASE_URL = "sqlite:///./test.db"

@pytest.fixture
def db_session():
    engine = create_engine(TEST_DATABASE_URL, connect_args={"check_same_thread": False})
    Base.metadata.create_all(bind=engine)
    TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    session = TestingSessionLocal()
    yield session
    session.close()
    Base.metadata.drop_all(bind=engine)

@pytest.fixture
def demo_user(db_session):
    user = User(
        email="test@trailguard.ai",
        hashed_password=hash_password("test1234"),
        display_name="Test User",
        role="analyst",
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    return user
