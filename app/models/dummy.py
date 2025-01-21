# from sqlalchemy import Column, Integer, String
# from app.db.base_class import Base

# class Dummy(Base):
#     __tablename__ = "dummy"
#     id = Column(Integer, primary_key=True, index=True)
#     name = Column(String, nullable=False)


# import asyncio
# from sqlalchemy.ext.asyncio import AsyncSession
# from app.models.user import User
# from app.db.session import async_session

# async def test_user_creation():
#     async with async_session() as session:
#         user = User(name="John Doe", email="john.doe@example.com", hashed_password="hashedpw")
#         session.add(user)
#         await session.commit()

# asyncio.run(test_user_creation())
