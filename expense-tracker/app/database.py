from collections.abc import Generator
from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase,Session,sessionmaker

from app.config import settings

#Engine : manages db connection pool.
# creating it doesn't establish connection
engine  = create_engine(
    settings.database_url,
    pool_pre_ping=True,
)

#Base class for all SQLAlchemy ORM modles
class Base(DeclarativeBase):
    pass


#sessionlocal : a factory that creates individual db sessions
#Each request will eventually get it's own session
SessionLocal = sessionmaker(
    bind=engine,
    autoflush=False,
    autocommit=False,
)

def get_db() -> Generator[Session,None,None]:
    """ Provide a db session and always close it afterwards."""
    db = SessionLocal()

    try :
        yield db
    finally:
        db.close()


"""
This distinction is important when building database-backed APIs.
- Engine: manages connections and the connection pool.
- Session: tracks database operations for a unit of work, such as creating or updating a transaction.
- get_db() provides a session to endpoint n closes it when req is finished

yield makes get_db() a generator dependency which fastapi can manaage using Depends(get_db)
can use when we implement transaction
pool_pre_ping = 1 checks pooled connections before using them , helping sqlalchemy detect stale connections
"""

"""
    What's Base?
    sqlalchemy uses this calss to register ORM models and collect theri table definitions
    later Base.metadata will contain the table definitions for all models that inherit from it
    
"""