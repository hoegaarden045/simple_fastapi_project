from decimal import Decimal
from app.models import User, Wallet
from app.enums import CurrencyEnum


def test_get_total_balance_success(db_session, user, wallet, client, auth_headers):
    second_wallet = Wallet(name="cash", balance=150, user_id=user.id, currency=CurrencyEnum.RUB)
    db_session.add(second_wallet)
    db_session.commit()

    response = client.get("/api/v1/balance", headers=auth_headers)

    assert response.status_code == 200
    assert Decimal(str(response.json()["total_balance"])) == Decimal("350.0")


def test_get_balance_unauthorized(client):
    response = client.get("/api/v1/balance", headers={"Authorization": "Bearer notexists"})

    assert response.status_code == 401
    assert response.json()["detail"] == "Could not validate credentials"


def test_get_all_wallets_success(user, wallet, client, auth_headers):
    response = client.get("/api/v1/wallets", headers=auth_headers)

    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1
    assert data[0]["name"] == wallet.name
    assert data[0]["currency"] == CurrencyEnum.RUB.value


def test_create_wallet_success(client, user, auth_headers):
    wallet_name = "new_card"
    response = client.post(
        "/api/v1/wallets",
        json={"name": wallet_name, "initial_balance": 200.0, "currency": "rub"},
        headers=auth_headers,
    )

    assert response.status_code == 200
    assert response.json()["name"] == wallet_name


def test_create_exists_wallet(client, user, wallet, auth_headers):
    response = client.post(
        "/api/v1/wallets",
        json={"name": wallet.name, "initial_balance": 200.0},
        headers=auth_headers,
    )

    assert response.status_code == 400
    assert response.json()["detail"] == f"Wallet '{wallet.name}' already exists"


def test_create_wallet_with_empty_name(client, user, auth_headers):
    response = client.post(
        "/api/v1/wallets",
        json={"name": "   ", "initial_balance": 200.0},
        headers=auth_headers,
    )

    assert response.status_code == 422


def test_create_wallet_with_negative_balance(client, user, auth_headers):
    response = client.post(
        "/api/v1/wallets",
        json={"name": "test", "initial_balance": -200.0},
        headers=auth_headers,
    )

    assert response.status_code == 422


def test_create_wallet_unauthorized(client):
    response = client.post(
        "/api/v1/wallets",
        json={"name": "test", "initial_balance": 200.0},
        headers={"Authorization": "Bearer notexists"},
    )

    assert response.status_code == 401
