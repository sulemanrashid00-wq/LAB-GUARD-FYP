import os
import sys
import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from fastapi.testclient import TestClient

# Ensure backend root is on path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from app.main import app
from app.core.database import Base, get_db
from app.core.security import get_password_hash, create_access_token
from app.models.user import User
from app.models.lab import Lab

# Dedicated test SQLite in-memory database
SQLALCHEMY_DATABASE_URL = "sqlite:///:memory:"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False}
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


@pytest.fixture(scope="session", autouse=True)
def setup_test_db():
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)


@pytest.fixture(scope="function")
def db_session():
    connection = engine.connect()
    transaction = connection.begin()
    session = TestingSessionLocal(bind=connection)

    # Seed test lab if not present
    if not session.query(Lab).filter(Lab.code == "TEST-LAB-01").first():
        lab = Lab(
            name="Test IoT Research Lab",
            code="TEST-LAB-01",
            building="Engineering Hall",
            room_number="Room 101",
            capacity=25,
            is_active=True
        )
        session.add(lab)
        session.commit()

    yield session

    session.close()
    transaction.rollback()
    connection.close()


@pytest.fixture(scope="function")
def client(db_session):
    def override_get_db():
        try:
            yield db_session
        finally:
            pass

    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()


@pytest.fixture(scope="function")
def test_user(db_session):
    user = db_session.query(User).filter(User.username == "testoperator").first()
    if not user:
        user = User(
            username="testoperator",
            email="operator@example.com",
            hashed_password=get_password_hash("SecretPass123!"),
            full_name="Test Operator",
            role="operator",
            is_active=True,
        )
        db_session.add(user)
        db_session.commit()
        db_session.refresh(user)
    return user


@pytest.fixture(scope="function")
def test_admin(db_session):
    admin = db_session.query(User).filter(User.username == "testadmin").first()
    if not admin:
        admin = User(
            username="testadmin",
            email="admin@example.com",
            hashed_password=get_password_hash("AdminSecret123!"),
            full_name="Test Admin User",
            role="admin",
            is_active=True,
        )
        db_session.add(admin)
        db_session.commit()
        db_session.refresh(admin)
    return admin


@pytest.fixture(scope="function")
def user_token_headers(test_user):
    token = create_access_token(subject=test_user.id)
    return {"Authorization": f"Bearer {token}"}


@pytest.fixture(scope="function")
def admin_token_headers(test_admin):
    token = create_access_token(subject=test_admin.id)
    return {"Authorization": f"Bearer {token}"}

