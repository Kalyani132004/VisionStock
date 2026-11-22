# database.py - connect to the database using SQLAlchemy

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

from .config import DATABASE_URL

# SQLite needs one extra setting, MySQL does not
if DATABASE_URL.startswith("sqlite"):
    engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
else:
    # pool_pre_ping checks the connection before using it
    engine = create_engine(DATABASE_URL, pool_pre_ping=True)

SessionLocal = sessionmaker(bind=engine, autocommit=False, autoflush=False)

Base = declarative_base()


# Every API route that needs the database asks for this function.
# It opens a session and always closes it at the end.
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
