# Fastapi RLS

a package to provide row level security seamlessly to you `fastapi` app by extending `sqlalchemy`.

## Installation

#### Package

Not done yet

#### Source Code
After cloning the repo

install dependencies using poetry

```bash
poetry install
```

Look at the a main.py and models.py for a an example how to use it with FastAPI

```python
# models.py

from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship
from rls.schemas import Permissive, Operation, ExpressionTypes, Command
from rls.register_rls import register_rls
from rls.database import Base

# Register RLS policies
register_rls(Base)


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True)


class Item(Base):
    __tablename__ = "items"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, index=True)
    description = Column(String)
    owner_id = Column(Integer, ForeignKey("users.id"))

    owner = relationship("User")

    __rls_policies__ = [
        Permissive(
            condition_args={
                "comparator_name": "user_id",
                "operation": Operation.equality,
                "type": ExpressionTypes.integer,
                "column_name": "owner_id",
            },
            cmd=[Command.all],
        )
    ]

```

```python
# main.py

from fastapi import FastAPI, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from rls.database import get_async_session
from test.models import Item


app = FastAPI()


@app.get("/users/items")
async def get_users(db: AsyncSession = Depends(get_async_session)):
    stmt = select(Item)
    result = await db.execute(stmt)
    items = result.scalars().all()

    return items

```

#### Run Tests
No e2e tests done yet

## API
These functions provide a structured way to handle database sessions and enforce row-level security (RLS) in your application. If you're working with SQLAlchemy models and need a secure and efficient way to manage database access, here's how you can use them:

### `register_rls(Base: Type[DeclarativeMeta])`

This function is used to automatically apply Row-Level Security (RLS) policies to your SQLAlchemy models. From the user's perspective:
- **When to Use**: Call this function when setting up your SQLAlchemy models (typically during application initialization).
- **Purpose**: It ensures that RLS policies are applied after creating tables in the database. This helps enforce fine-grained access control, allowing you to control which rows of data users are allowed to access based on the defined policies.
- **How it Works**: It listens for table creation events and applies security policies automatically, so you don't have to manually enforce them for each table.

### `get_sync_session(request: Request)`

This function provides a synchronous session for interacting with the database. You can use it to execute SQL statements or queries in your API routes or service functions:
- **When to Use**: Use this function when working with synchronous code, such as in FastAPI routes that do not use `async` functionality.
- **How it Works**: It creates a session, applies any necessary set statements (e.g., for tenant-specific data filtering), and provides it for use in the current request context. Once the work is done, it automatically handles cleanup (via Python's context management).

### `get_async_session(request: Request)`

This function is similar to `get_sync_session`, but for asynchronous code:
- **When to Use**: Use this function when working in an asynchronous context (e.g., with `async def` routes in FastAPI).
- **How it Works**: It provides an asynchronous session that allows you to interact with the database without blocking the event loop. Like the sync version, it applies RLS policies or other session-level statements and automatically handles the session's lifecycle.


## Examples

using the models.py and main.py found in source code installation

you can send a request with curl for example :
```bash
curl -H "user_id: 2" localhost:8000/users/items
```
it will return only the items owned by owner whose id is 2 as specified in the policy
```json
[
    {
        "description": "Description for item3",
        "owner_id": 2,
        "id": 3,
        "title": "item3"
    },
    {
        "description": "Description for item4",
        "owner_id": 2,
        "id": 4,
        "title": "item4"
    }
]
```
noting that the items table contains
```json
[
    {
        "description": "Description for item1",
        "owner_id": 1,
        "id": 1,
        "title": "item1"
    },
    {
        "description": "Description for item2",
        "owner_id": 1,
        "id": 2,
        "title": "item2"
    },
    {
        "description": "Description for item3",
        "owner_id": 2,
        "id": 3,
        "title": "item3"
    },
    {
        "description": "Description for item4",
        "owner_id": 2,
        "id": 4,
        "title": "item4"
    }
]
```

## License

[MIT](LICENSE)
