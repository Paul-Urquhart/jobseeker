from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, DeclarativeBase
from dotenv import load_dotenv
import os

load_dotenv()

DATABASE_HOST = os.getenv("DATABASE_HOST")
DATABASE_PASSWORD = os.getenv("DATABASE_PASSWORD")
DATABASE_USER = os.getenv("DATABASE_USER")
DATABASE = os.getenv("DATABASE")

DB_CONNECTION_STRING = f"postgresql+psycopg2://{DATABASE_USER}:{DATABASE_PASSWORD}@{DATABASE_HOST}:5432/{DATABASE}"

engine = create_engine(
    DB_CONNECTION_STRING
)

Session = sessionmaker(bind=engine)

class Base(DeclarativeBase):
    pass