def test_user_create_success(client):
    response = client.post(
        "/api/v1/users",
        json={"login": "test"}
    )

    assert response.status_code == 200

def test_create_exists_user(user, client):
    response = client.post(
        "/api/v1/users",
        json={"login": user.login}
    )

    assert response.status_code == 400
    assert response.json()["detail"] == "User already exists"

def test_get_me_success(user, client):
    response = client.get(
        "/api/v1/users/me",
        headers={"Authorization": f"Bearer {user.login}"}
    )

    assert response.status_code == 200
    assert response.json()["login"] == user.login
    assert "id" in response.json()

def test_get_me_fake_token(client):
    response = client.get(
        "/api/v1/users/me",
        headers={"Authorization": f"Bearer fake_token"}
    )

    assert response.status_code == 401
    assert response.json()["detail"] == "Unauthorized"
