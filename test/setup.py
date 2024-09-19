# sync_setup.py
from sqlalchemy import create_engine
from .models import Base

DATABASE_URL = "postgresql://user:password@localhost/session"
# Use a synchronous engine for schema creation
engine = create_engine(DATABASE_URL)


def setup_database():
    # Create tables
    Base.metadata.create_all(engine)


if __name__ == "__main__":
    setup_database()
