from fastapi import status


def test_register_user(client):
    response = client.post(
        "/api/v1/auth/register",
        json={
            "username": "newstudent",
            "email": "student@labguard.org",
            "password": "Password123!",
            "full_name": "Student Researcher",
            "role": "student"
        }
    )
    assert response.status_code == status.HTTP_201_CREATED
    data = response.json()
    assert data["success"] is True
    assert data["data"]["username"] == "newstudent"
    assert data["data"]["email"] == "student@labguard.org"


def test_login_successful(client, test_user):
    response = client.post(
        "/api/v1/auth/login",
        json={
            "username_or_email": test_user.username,
            "password": "SecretPass123!"
        }
    )
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert "access_token" in data
    assert "refresh_token" in data
    assert data["token_type"] == "bearer"


def test_login_invalid_password(client, test_user):
    response = client.post(
        "/api/v1/auth/login",
        json={
            "username_or_email": test_user.username,
            "password": "WrongPassword!"
        }
    )
    assert response.status_code == status.HTTP_401_UNAUTHORIZED


def test_get_current_user_profile(client, user_token_headers, test_user):
    response = client.get("/api/v1/auth/me", headers=user_token_headers)
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["success"] is True
    assert data["data"]["username"] == test_user.username

