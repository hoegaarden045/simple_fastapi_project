from decimal import Decimal
import pytest
from app.models import User, Wallet
from app.enums import OperationType, CurrencyEnum


@pytest.mark.parametrize("endpoint", ["/api/v1/operations/expense", "/api/v1/operations/income"])
def test_operations_negative_amount_validation(user, wallet, client, endpoint, auth_headers):
    response = client.post(
        endpoint,
        json={"wallet_name": wallet.name, "amount": -100.0, "description": "Test"},
        headers=auth_headers,
    )

    assert response.status_code == 422


@pytest.mark.parametrize("endpoint", ["/api/v1/operations/expense", "/api/v1/operations/income"])
def test_operations_empty_wallet_name(user, client, endpoint, auth_headers):
    response = client.post(
        endpoint,
        json={"wallet_name": "   ", "amount": 100.0, "description": "Test"},
        headers=auth_headers,
    )

    assert response.status_code == 422


@pytest.mark.parametrize("endpoint", ["/api/v1/operations/expense", "/api/v1/operations/income"])
def test_operations_wallet_not_found(user, client, endpoint, auth_headers):
    response = client.post(
        endpoint,
        json={"wallet_name": "ghost_card", "amount": 50.0, "description": "Food"},
        headers=auth_headers,
    )

    assert response.status_code == 404


@pytest.mark.parametrize("endpoint", ["/api/v1/operations/expense", "/api/v1/operations/income"])
def test_operations_unauthorized(client, endpoint):
    response = client.post(
        endpoint,
        json={"wallet_name": "card", "amount": 50.0, "description": "Food"},
        headers={"Authorization": "Bearer notexists"},
    )

    assert response.status_code == 401


def test_add_expense_success(user, wallet, client, auth_headers):
    response = client.post(
        "/api/v1/operations/expense",
        json={"wallet_name": wallet.name, "amount": 50.0, "description": "Food"},
        headers=auth_headers,
    )

    assert response.status_code == 200
    assert Decimal(str(response.json()["amount"])) == Decimal("50.0")


def test_add_expense_insufficient_funds(user, wallet, client, auth_headers):
    response = client.post(
        "/api/v1/operations/expense",
        json={"wallet_name": wallet.name, "amount": 500.0, "description": "Food"},
        headers=auth_headers,
    )

    assert response.status_code == 400


def test_add_income_success(user, wallet, client, auth_headers):
    response = client.post(
        "/api/v1/operations/income",
        json={"wallet_name": wallet.name, "amount": 50.0, "description": "Salary"},
        headers=auth_headers,
    )

    assert response.status_code == 200
    assert Decimal(str(response.json()["amount"])) == Decimal("50.0")


def test_get_operations_list_success(user, wallet, client, auth_headers):
    client.post(
        "/api/v1/operations/income",
        json={"wallet_name": wallet.name, "amount": 100.0, "description": "Bonus"},
        headers=auth_headers,
    )

    response = client.get("/api/v1/operations", headers=auth_headers)
    assert response.status_code == 200
    assert len(response.json()) >= 1


def test_transfer_between_wallets_success(db_session, user, wallet, client, auth_headers):
    second_wallet = Wallet(name="cash", balance=50, user_id=user.id, currency=CurrencyEnum.RUB)
    db_session.add(second_wallet)
    db_session.commit()
    db_session.refresh(second_wallet)

    response = client.post(
        "/api/v1/operations/transfer",
        json={"from_wallet_id": wallet.id, "to_wallet_id": second_wallet.id, "amount": 100.0},
        headers=auth_headers,
    )

    assert response.status_code == 200
    assert Decimal(str(response.json()["amount"])) == Decimal("100.0")

    db_session.refresh(wallet)
    db_session.refresh(second_wallet)
    assert wallet.balance == Decimal("100.0")
    assert second_wallet.balance == Decimal("150.0")
