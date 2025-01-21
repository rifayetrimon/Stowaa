import asyncio
from sqlalchemy.ext.asyncio import AsyncEngine, AsyncSession
from app.db.session import engine
from app.db.base_class import Base
# from app.models.dummy import Dummy



async def init_db():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)


    # for dummy 
    # async with AsyncSession(engine) as session:
    #     dummy_data = Dummy(name="Test Entry")
    #     session.add(dummy_data)
    #     await session.commit()

    # print("Database initialized and dummy data inserted.")

if __name__ == "__main__":
    asyncio.run(init_db())