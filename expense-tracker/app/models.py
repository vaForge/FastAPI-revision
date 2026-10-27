from datetime import date,datetime
from decimal import Decimal

from sqlalchemy import (
    CheckConstraint,
    Date,
    DateTime,
    Integer,
    Numeric,
    String,
    Text,
    func,
)

from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base

class Transaction(Base):
    """Represents one income or expense transaction in PostgreSQL."""
    __tablename__ = "transactions"
    #DB-level constraints for valid transaction records.
    __table_args__ = (
        CheckConstraint(
            "transaction_type IN ('income','expense')",
            name="ck_transactions_type",
        ),
        CheckConstraint(
            "amount > 0",
            name="ck_transactions_amount_positive",
        ),   
    )

    # Primary key : Postgres generated id for each row
    id : Mapped[int] = mapped_column(Integer,primary_key=True)
    # short name for transaction
    title: Mapped[str] = mapped_column(String(200),nullable=False)
    # Use Decimal and Numeric for monetary values, not float.
    amount: Mapped[Decimal] = mapped_column(Numeric(12, 2), nullable=False)
    # Restricted to 'income' or 'expense' by the table constraint.
    transaction_type: Mapped[str] = mapped_column(String(10), nullable=False)
    # Examples: Food, Travel, Education, Salary.
    category: Mapped[str] = mapped_column(String(100), nullable=False)
    # Optional details about the transaction.
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    # The date e transaction happened.
    transaction_date: Mapped[date] = mapped_column(Date, nullable=False)

    #timestamp when row created
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )
    
