
from datetime import date
from decimal import Decimal

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.models import Transaction
from app.schemas import TransactionCreate, TransactionUpdate


# Application-level exception, independent of HTTP.
class TransactionNotFoundError(Exception):
    pass


def create_transaction(
    db: Session,
    payload: TransactionCreate,
) -> Transaction:
    # Convert validated request data into a database model.
    transaction = Transaction(**payload.model_dump())

    try:
        db.add(transaction)
        db.commit()
        db.refresh(transaction)  # Load the generated database ID.
    except Exception:
        db.rollback()
        raise

    return transaction


def list_transactions(
    db: Session,
    transaction_type: str | None = None,
    category: str | None = None,
    start_date: date | None = None,
    end_date: date | None = None,
    skip: int = 0,
    limit: int = 20,
) -> list[Transaction]:
    statement = select(Transaction)

    # Add only the filters requested by the client.
    if transaction_type is not None:
        statement = statement.where(
            Transaction.transaction_type == transaction_type
        )

    if category is not None:
        statement = statement.where(Transaction.category == category)

    if start_date is not None:
        statement = statement.where(
            Transaction.transaction_date >= start_date
        )

    if end_date is not None:
        statement = statement.where(
            Transaction.transaction_date <= end_date
        )

    statement = (
        statement
        .order_by(
            Transaction.transaction_date.desc(),
            Transaction.id.desc(),
        )
        .offset(skip)
        .limit(limit)
    )

    return list(db.scalars(statement).all())


def get_transaction(db: Session, transaction_id: int) -> Transaction:
    transaction = db.get(Transaction, transaction_id)

    if transaction is None:
        raise TransactionNotFoundError("Transaction not found")

    return transaction


def update_transaction(
    db: Session,
    transaction_id: int,
    payload: TransactionUpdate,
) -> Transaction:
    transaction = get_transaction(db, transaction_id)

    # Do not overwrite fields that the client omitted.
    updates = payload.model_dump(exclude_unset=True)

    for field, value in updates.items():
        setattr(transaction, field, value)

    try:
        db.commit()
        db.refresh(transaction)
    except Exception:
        db.rollback()
        raise

    return transaction


def delete_transaction(db: Session, transaction_id: int) -> None:
    transaction = get_transaction(db, transaction_id)

    try:
        db.delete(transaction)
        db.commit()
    except Exception:
        db.rollback()
        raise


def transaction_summary(db: Session) -> dict[str, Decimal]:
    # PostgreSQL calculates the totals; Python assembles the response.
    statement = select(
        Transaction.transaction_type,
        func.sum(Transaction.amount),
    ).group_by(Transaction.transaction_type)

    totals = {
        "income": Decimal("0.00"),
        "expense": Decimal("0.00"),
    }

    for transaction_type, amount in db.execute(statement):
        totals[transaction_type] = amount

    return {
        "total_income": totals["income"],
        "total_expenses": totals["expense"],
        "balance": totals["income"] - totals["expense"],
    }
