from decimal import Decimal

import pytest
from app.models import User, Wallet

@pytest.mark.parametrize("endpoint", ["/api/v1/operations/expense", "/api/v1/operations/income"])
def test_operations_negative_amount_validation(user, wallet, client, endpoint):
    # Arrange
    # Act
    response = client.post(
        endpoint, 
        json={
            "wallet_name": wallet.name,
            "amount": -100.0, 
            "description": "Test"
        },
        headers={"Authorization": f"Bearer {user.login}"}
    )

    # Assert
    assert response.status_code == 422
    assert "Amount must be positive" in response.json()["detail"][0]["msg"]

@pytest.mark.parametrize("endpoint", ["/api/v1/operations/expense", "/api/v1/operations/income"])
def test_operations_empty_wallet_name(user, client, endpoint):
    # Act
    response = client.post(
        endpoint, 
        json={
            "wallet_name": "   ",
            "amount": 100.0, 
            "description": "Test"
        },
        headers={"Authorization": f"Bearer {user.login}"}
    )

    # Assert
    assert response.status_code == 422
    assert "wallet name cannot be empty" in response.json()["detail"][0]["msg"]

@pytest.mark.parametrize("endpoint", ["/api/v1/operations/expense", "/api/v1/operations/income"])
def test_operations_wallet_not_found(user, client, endpoint):
    response = client.post(
        endpoint,
        json={
            "wallet_name": "ghost_card",
            "amount": 50.0,
            "description": "Food"
        },
        headers={"Authorization": f"Bearer {user.login}"}
    )

    assert response.status_code == 404
    assert response.json()["detail"] == "Wallet 'ghost_card' not found"

@pytest.mark.parametrize("endpoint", ["/api/v1/operations/expense", "/api/v1/operations/income"])
def test_operations_unauthorized(client, endpoint):
    response = client.post(
        endpoint,
        json={
            "wallet_name": "card",
            "amount": 50.0,
            "description": "Food"
        },
        headers={"Authorization": "Bearer notexists"}
    )

    assert response.status_code == 401
    assert response.json()["detail"] == "Unauthorized"

def test_add_expense_success(user, wallet, client):
    # Act
    response = client.post(
        "/api/v1/operations/expense",
        json={
            "wallet_name": wallet.name,
            "amount": 50.0,
            "description": "Food"
        },
        headers={"Authorization": f"Bearer {user.login}"}
    )

    # Assert
    assert response.status_code == 200
    assert response.json()["message"] == "Expense added"
    assert response.json()["wallet"] == wallet.name 
    assert Decimal(str(response.json()["amount"])) == Decimal(50)
    assert Decimal(str(response.json()["new_balance"])) == Decimal(150)
    assert response.json()["description"] == "Food"

def test_add_expense_insufficient_funds(user, wallet, client):
    response = client.post(
        "/api/v1/operations/expense",
        json={
            "wallet_name": wallet.name,
            "amount": 500.0,
            "description": "Food"
        },
        headers={"Authorization": f"Bearer {user.login}"}
    )

    assert response.status_code == 400
    assert response.json()["detail"] == f"Insufficient funds. Available: {wallet.balance}"

def test_add_income_success(user, wallet, client):
    # Act
    response = client.post(
        "/api/v1/operations/income",
        json={
            "wallet_name": wallet.name,
            "amount": 50.0,
            "description": "Food"
        },
        headers={"Authorization": f"Bearer {user.login}"}
    )

    # Assert
    assert response.status_code == 200
    assert response.json()["message"] == "Income added"
    assert response.json()["wallet"] == wallet.name 
    assert Decimal(str(response.json()["amount"])) == Decimal(50)
    assert Decimal(str(response.json()["new_balance"])) == Decimal(250)
    assert response.json()["description"] == "Food"
