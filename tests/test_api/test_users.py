def test_user_create_success(client):
    response = client.post("/api/v1/users", json={"login": "newtest", "password": "password123"})

    assert response.status_code == 200
    assert response.json()["login"] == "newtest"


def test_create_exists_user(user, client):
    response = client.post("/api/v1/users", json={"login": user.login, "password": "password123"})

    assert response.status_code == 400
    assert response.json()["detail"] == "User already exists"


def test_login_success(user, client):
    response = client.post(
        "/api/v1/users/login",
        data={"username": user.login, "password": "testpassword"},
        headers={"Content-Type": "application/x-www-form-urlencoded"},
    )

    assert response.status_code == 200
    assert "access_token" in response.json()
    assert response.json()["token_type"] == "bearer"


def test_login_wrong_password(user, client):
    response = client.post("/api/v1/users/login", data={"username": user.login, "password": "wrongpassword"})

    assert response.status_code == 401
    assert response.json()["detail"] == "Incorrect username or password"


def test_get_me_success(user, client, auth_headers):
    response = client.get("/api/v1/users/me", headers=auth_headers)

    assert response.status_code == 200
    assert response.json()["login"] == user.login
    assert "id" in response.json()


def test_get_me_fake_token(client):
    response = client.get("/api/v1/users/me", headers={"Authorization": "Bearer fake_token"})

    assert response.status_code == 401
    assert response.json()["detail"] == "Could not validate credentials"
