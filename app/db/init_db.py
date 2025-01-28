import asyncio
from sqlalchemy.ext.asyncio import AsyncEngine, AsyncSession
from app.db.session import engine, async_session
from app.db.base_class import Base

# all models import here
from app.models.user import User
from app.models.wishlist import Wishlist
from app.models.address import Address
from app.models.product import Product
from app.models.category import Category
from app.models.cart import Cart
from app.models.order import Order
from app.models.review import Review

async def init_db():
    try:
        async with engine.begin() as conn:
            # Create all tables
            await conn.run_sync(Base.metadata.create_all)
            print("All tables created successfully")
    except Exception as e:
        print(f"An error occurred during database initialization: {e}")
        raise
    finally:
        await engine.dispose()
        print("Database connection closed")

def init():
    """Wrapper function to run the async init_db function"""
    asyncio.run(init_db())

if __name__ == "__main__":
    print("Starting database initialization...")
    init()
    print("Database initialization completed")