import pytest

from fastapi.testclient import TestClient

from app.main import app

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from app.config import settings
from app.database import get_db, Base

from app.oauth2 import create_jwt_token

SQLALCHEMY_DATABASE_URL = f"postgresql://{settings.DATABASE_ROOT_USER}:{settings.DATABASE_ROOT_PASSWORD}@{settings.DATABASE_URL}:{settings.DATABASE_PORT}/{settings.TEST_DATABASE_NAME}"
engine = create_engine(SQLALCHEMY_DATABASE_URL)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)



@pytest.fixture(scope="function")
def session():
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)

    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()




@pytest.fixture(scope="function")
def client(session):
    def override_get_db():
        try:
            yield session
        finally:
            session.close()
        
    app.dependency_overrides[get_db] = override_get_db

    yield TestClient(app)


    
@pytest.fixture(scope="function")
def test_user(client):
    user_data = {
        "username": "m",
        "email": "m@email.com",
        "password": "password123",
    }
    res = client.post("/users", json=user_data)
    assert res.status_code == 201
    new_user = res.json()
    new_user["password"] = user_data["password"]
    return new_user


@pytest.fixture(scope="function")
def token(test_user):
    return create_jwt_token(data={"user_id": test_user['id']})


@pytest.fixture
def authorized_client(client, token):
    client.headers = {
        **client.headers ,
        "Authorization": f"Bearer {token}"
    }
    return client

