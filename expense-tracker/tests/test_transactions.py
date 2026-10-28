
from decimal import Decimal

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine, delete
from sqlalchemy.orm import sessionmaker

from app.config import settings
from app.database import Base, get_db
from app.main import app
from app.models import Transaction


# Reuse the development connection settings but target a separate database.
test_engine = create_engine(
    settings.database_url.set(database="expense_tracker_test"),
    pool_pre_ping=True,
)

TestSessionLocal = sessionmaker(
    bind=test_engine,
    autoflush=False,
    autocommit=False,
)

# Register the model and create tables only in the test database.
Base.metadata.create_all(bind=test_engine)


def override_get_db():
    """Give API requests a session connected to the test database."""
    db = TestSessionLocal()
    try:
        yield db
    finally:
        db.close()


# Replace the application's database dependency during these tests.
app.dependency_overrides[get_db] = override_get_db
client = TestClient(app)


@pytest.fixture(autouse=True)
def clean_transactions():
    """Ensure each test starts and ends with an empty transaction table."""
    with TestSessionLocal() as db:
        db.execute(delete(Transaction))
        db.commit()

    yield

    with TestSessionLocal() as db:
        db.execute(delete(Transaction))
        db.commit()


def create_transaction(
    title="Groceries",
    amount="120.50",
    transaction_type="expense",
    category="Food",
):
    """Helper to create a transaction through the real HTTP endpoint."""
    response = client.post(
        "/transactions",
        json={
            "title": title,
            "amount": amount,
            "transaction_type": transaction_type,
            "category": category,
            "transaction_date": "2026-10-28",
        },
    )
    assert response.status_code == 201
    return response.json()


def test_create_transaction():
    response = client.post(
        "/transactions",
        json={
            "title": "Groceries",
            "amount": "120.50",
            "transaction_type": "expense",
            "category": "Food",
            "transaction_date": "2026-10-28",
        },
    )

    assert response.status_code == 201
    assert response.json()["title"] == "Groceries"
    assert Decimal(response.json()["amount"]) == Decimal("120.50")


def test_filter_transactions():
    create_transaction()
    create_transaction(
        title="Salary",
        amount="1000.00",
        transaction_type="income",
        category="Work",
    )

    response = client.get(
        "/transactions",
        params={"transaction_type": "expense"},
    )

    assert response.status_code == 200
    assert len(response.json()) == 1
    assert response.json()[0]["title"] == "Groceries"


def test_update_transaction():
    transaction = create_transaction()

    response = client.patch(
        f"/transactions/{transaction['id']}",
        json={"amount": "150.00"},
    )

    assert response.status_code == 200
    assert response.json()["title"] == "Groceries"
    assert Decimal(response.json()["amount"]) == Decimal("150.00")


def test_delete_transaction():
    transaction = create_transaction()
    transaction_id = transaction["id"]

    response = client.delete(f"/transactions/{transaction_id}")

    assert response.status_code == 204

    missing = client.get(f"/transactions/{transaction_id}")
    assert missing.status_code == 404


def test_summary():
    create_transaction(
        title="Salary",
        amount="1000.00",
        transaction_type="income",
        category="Work",
    )
    create_transaction()

    response = client.get("/transactions/summary")
    summary = response.json()

    assert response.status_code == 200
    assert Decimal(str(summary["total_income"])) == Decimal("1000.00")
    assert Decimal(str(summary["total_expenses"])) == Decimal("120.50")
    assert Decimal(str(summary["balance"])) == Decimal("879.50")


def test_invalid_amount_is_rejected():
    response = client.post(
        "/transactions",
        json={
            "title": "Invalid expense",
            "amount": "0",
            "transaction_type": "expense",
            "category": "Food",
            "transaction_date": "2026-10-28",
        },
    )

    assert response.status_code == 422
