from fastapi import FastAPI,HTTPException,Request
from fastapi.responses import JSONResponse
from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError
import logging


from app.database import engine
from app.service import TransactionNotFoundError
from app.router import router as transactions_router

app = FastAPI()
logger = logging.getLogger(__name__)
app.include_router(transactions_router)

@app.get("/",tags= ["Health"])
def home():
    return {"message":"Expense Tracker API is running"}

@app.get("/health/db",tags=["Health"])
def check_database():
    #Open a conn and execute minimal sql query
    try: 
        with engine.connect() as connection:
            connection.execute(text("SELECT 1"))

    except SQLAlchemyError as exc :
        # return a service unaval response if the DB is unreachable
        logger.exception("Database health check failed")
        raise HTTPException(
            status_code=503,
            detail="Database is unavailable",
        ) from exc

    return {"database":"connected"}


@app.exception_handler(TransactionNotFoundError)
async def transaction_not_found_handler(
    request: Request,
    exc : TransactionNotFoundError,
):
    return JSONResponse(
        status_code=404,
        content={"detail",str(exc)},
    )