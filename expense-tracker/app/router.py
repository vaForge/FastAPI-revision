
from datetime import date

from fastapi import APIRouter, Depends, Query, Response, status
from sqlalchemy.orm import Session

from app.database import get_db
from app import service
from app.schemas import (
    TransactionCreate,
    TransactionResponse,
    TransactionUpdate,
)


router = APIRouter(prefix="/transactions", tags=["Transactions"])


@router.post(
    "",
    response_model=TransactionResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_transaction(
    payload: TransactionCreate,
    db: Session = Depends(get_db),
):
    return service.create_transaction(db, payload)


@router.get("", response_model=list[TransactionResponse])
def list_transactions(
    transaction_type: str | None = Query(
        default=None,
        pattern="^(income|expense)$",
    ),
    category: str | None = None,
    start_date: date | None = None,
    end_date: date | None = None,
    skip: int = Query(default=0, ge=0),
    limit: int = Query(default=20, ge=1, le=100),
    db: Session = Depends(get_db),
):
    return service.list_transactions(
        db,
        transaction_type=transaction_type,
        category=category,
        start_date=start_date,
        end_date=end_date,
        skip=skip,
        limit=limit,
    )


@router.get("/summary")
def transaction_summary(db: Session = Depends(get_db)):
    return service.transaction_summary(db)


@router.get("/{transaction_id}", response_model=TransactionResponse)
def get_transaction(
    transaction_id: int,
    db: Session = Depends(get_db),
):
    return service.get_transaction(db, transaction_id)


@router.patch("/{transaction_id}", response_model=TransactionResponse)
def update_transaction(
    transaction_id: int,
    payload: TransactionUpdate,
    db: Session = Depends(get_db),
):
    return service.update_transaction(db, transaction_id, payload)


@router.delete(
    "/{transaction_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
def delete_transaction(
    transaction_id: int,
    db: Session = Depends(get_db),
):
    service.delete_transaction(db, transaction_id)
    return Response(status_code=status.HTTP_204_NO_CONTENT)
