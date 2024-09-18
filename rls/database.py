from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker
from rls.schemas import Policy
from fastapi import Request
from fastapi.datastructures import Headers
from sqlalchemy import text, create_engine

#--------------------------------------Set RLS variables-----------------------------#

def _get_set_statements(headers: Headers) -> str:    
    # must be setup for the rls_policies key to be set
    queries = []

    Base.metadata.info.setdefault("rls_policies", dict())
    for mapper in Base.registry.mappers:
        if not hasattr(mapper.class_, "__rls_policies__"):
            continue
        table_name = mapper.tables[0].fullname
        policies: list[Policy] = mapper.class_.__rls_policies__

        for policy in policies:
            db_var_name = policy.get_db_var_name(table_name)
            comparator_name = policy.condition_args["comparator_name"]
            comparator_value = headers.get(comparator_name)

            if(comparator_value is None):
                continue

            temp_query = f"SET LOCAL {db_var_name} = {comparator_value};"

            queries.append(temp_query)

        
    if(len(queries) == 0):
        return ""
    combined_query = text('\n'.join(queries))  # Combine queries into a single string

    return combined_query



#--------------------------------------Base Initialization-----------------------------#


# Base class for our models
Base = declarative_base()


#--------------------------------------Engines Initialization-----------------------------#


ASYNC_DATABASE_URL = "postgresql+asyncpg://my_user:secure_password@localhost/session"

SYNC_DATABASE_URL = "postgresql://my_user:secure_password@localhost/session"


# TODO: DATABASE_URL should be an environment variable be it SYNC or ASYNC
# SQLAlchemy engine
async_engine = create_async_engine(ASYNC_DATABASE_URL)

# SQLAlchemy session
AsyncSessionLocal = sessionmaker(
    bind=async_engine,
    class_=AsyncSession,  # Specify that the session should be async
    expire_on_commit=False,
)


sync_engine = create_engine(SYNC_DATABASE_URL)

SyncSessionLocal = sessionmaker(
    bind=sync_engine,
    class_= Session,
    expire_on_commit=False,
)



#--------------------------------------Deps injection functions-----------------------------#


def get_sync_session(request: Request):
    with SyncSessionLocal() as session:
        stmts = _get_set_statements(request.headers)
        if(stmts != ""):
             session.execute(stmts)
        yield session
        
     

# Dependency to get DB session in routes
async def get_async_session(request: Request):
    async with AsyncSessionLocal() as session:
        stmts = _get_set_statements(request.headers)
        if(stmts != ""):
            await session.execute(stmts)
        yield session
