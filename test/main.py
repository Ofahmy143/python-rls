from fastapi import FastAPI, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy import text

from database import get_db
from models import Item


app = FastAPI()

@app.get("/users/{user_id}/items")
async def get_users(user_id, db: AsyncSession = Depends(get_db)):

    items = None
    async with db as session:
        print('session', session)
        stmt = text(f"SET LOCAL app.current_user_id = {user_id}")
        print('stmt', stmt)
        await db.execute(stmt)

        # Retrieve the parameter value
        get_param_stmt = text("SELECT current_setting('app.current_user_id')")
        result = await db.execute(get_param_stmt)
        current_user_id = result.scalar()  # Get the single value
        print('after: current_user_id', current_user_id)

        stmt = select(Item)
        result = await db.execute(stmt)
        items = result.scalars().all()


    return items