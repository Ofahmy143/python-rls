from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker

DATABASE_URL = "postgresql+asyncpg://my_user:secure_password@localhost/session"




# SQLAlchemy engine
engine = create_async_engine(DATABASE_URL)

# SQLAlchemy session
AsyncSessionLocal = sessionmaker(
    bind=engine,
    class_=AsyncSession,  # Specify that the session should be async
    expire_on_commit=False,
)
# Base class for our models
Base = declarative_base()

# Dependency to get DB session in routes
async def get_db():
    async with AsyncSessionLocal() as session:
        yield session
