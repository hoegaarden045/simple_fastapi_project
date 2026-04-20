from decimal import Decimal
from urllib import response
from app.models import  User, Wallet


def test_wallet_exists(user, client):
    response = client.get(
        "/api/v1/balance",
        params={"wallet_name": "card"},
        headers={"Authorization": f"Bearer {user.login}"}
    )

    assert response.status_code == 404
    assert response.json()["detail"] == f"wallet 'card' not found"


def test_get_wallets_unauthorized(client):
    response = client.get(
        "/api/v1/balance",
        params={"wallet_name": "card"},
        headers={"Authorization": "Bearer notexists"}
    )

    assert response.status_code == 401
    assert response.json()["detail"] == "Unauthorized"

def test_get_balance_success(user, wallet, client):
    response = client.get(
        "/api/v1/balance",
        params={"wallet_name": wallet.name},
        headers={"Authorization": f"Bearer {user.login}"}
    )

    assert response.status_code == 200
    assert response.json()["wallet"] == wallet.name
    assert Decimal(str(response.json()["balance"])) == Decimal(200)

def test_get_total_balance_success(db_session, user, wallet, client):
    second_wallet = Wallet(
        name = "cash",
        balance = 150,
        user_id = user.id
    )
    db_session.add(second_wallet)
    db_session.commit()

    response = client.get(
        "/api/v1/balance",
        headers={"Authorization": f"Bearer {user.login}"}
    )

    assert response.status_code == 200
    assert Decimal(str(response.json()["total_balance"])) == Decimal(350) 

def test_get_another_user_wallet( db_session, wallet, client):
    second_user = User(login="test2")
    db_session.add(second_user)
    db_session.commit()

    response = client.get(
        "/api/v1/balance",
        params={"wallet_name": wallet.name},
        headers={"Authorization": f"Bearer {second_user.login}"}
    )

    assert response.status_code == 404
    assert response.json()["detail"] == f"wallet '{wallet.name}' not found"

def test_create_wallet_success(client, user):
    
    wallet_name = "card"

    response = client.post(
        "/api/v1/wallets",
        json={
            "name": wallet_name,
            "initial_balance": 200.0
        },
        headers={"Authorization": f"Bearer {user.login}"}
    )

    assert response.status_code == 200
    assert response.json()["message"] == f"wallet '{wallet_name}' created"
    assert response.json()["wallet"] == wallet_name
    assert Decimal(str(response.json()["balance"])) == Decimal(200)

def test_create_exists_wallet(client, user, wallet):
    response = client.post(
        "/api/v1/wallets",
        json={
            "name": wallet.name,
            "initial_balance": 200.0
        },
        headers={"Authorization": f"Bearer {user.login}"}
    )

    assert response.status_code == 400
    assert response.json()["detail"] == f"Wallet '{wallet.name}' already exists"

def test_create_wallet_with_empty_name(client, user):
    response = client.post(
        "/api/v1/wallets",
        json={
            "name": "   ",
            "initial_balance": 200.0
        },
        headers={"Authorization": f"Bearer {user.login}"}
    )

    assert response.status_code == 422
    assert "Wallet name cannot be empty" in response.json()["detail"][0]["msg"]

def test_create_wallet_with_negative_balance(client, user):
    response = client.post(
        "/api/v1/wallets",
        json={
            "name": "test",
            "initial_balance": -200.0
        },
        headers={"Authorization": f"Bearer {user.login}"}
    )

    assert response.status_code == 422
    assert "Initial balance cannot be negative" in response.json()["detail"][0]["msg"]

def test_create_wallet_unauthorized(client):
    response = client.post(
        "/api/v1/wallets",
        json={
            "name": "test",
            "initial_balance": 200.0
        },
        headers={"Authorization": f"Bearer notexists"}
    )

    assert response.status_code == 401
    assert response.json()["detail"] == "Unauthorized"

