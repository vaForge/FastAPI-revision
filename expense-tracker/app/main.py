from fastapi import FastAPI,HTTPException
from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError
import logging


from app.database import engine

app = FastAPI()
logger = logging.getLogger(__name__)

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