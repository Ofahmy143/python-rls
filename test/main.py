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
