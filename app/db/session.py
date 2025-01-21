from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker
from app.core.config import settings


# database engine

engine = create_async_engine(settings.DATABASE_URL, echo=True, future=True)


# session maker 
async_session = sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,
)

# get db session
    
async def get_db():
    async with async_session() as session:
        yield session