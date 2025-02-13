# import pytest
# from sqlalchemy.ext.asyncio import AsyncSession
# from app.models.category import Category
# from app.schemas.category import CategoryCreate, CategoryResponse, CategoryListResponse, CategoryDetailsResponse, CategoryUpdate
# from app.services.category import CategoryService 

# @pytest.fixture
# def new_category_data():
#     return CategoryCreate(name="Tech", description="Technology related events", user_id=1)

# @pytest.mark.asyncio
# async def test_create_category(db_session: AsyncSession, new_category_data: CategoryCreate):
#     category = await CategoryService.create_category(db_session, new_category_data)
#     assert category is not None
#     assert category.name == new_category_data.name
#     assert category.description == new_category_data.description

# @pytest.mark.asyncio
# async def test_get_category(db_session: AsyncSession, new_category_data: CategoryCreate):
#     category = await CategoryService.create_category(db_session, new_category_data)
#     fetched_category = await CategoryService.get_category(db_session, category.id)
#     assert fetched_category is not None
#     assert fetched_category.id == category.id
#     assert fetched_category.name == category.name

# @pytest.mark.asyncio
# async def test_update_category(db_session: AsyncSession, new_category_data: CategoryCreate):
#     category = await CategoryService.create_category(db_session, new_category_data)
#     update_data = CategoryUpdate(name="Updated Tech", description="Updated description")
#     updated_category = await CategoryService.update_category(db_session, category.id, update_data)
#     assert updated_category is not None
#     assert updated_category.name == "Updated Tech"
#     assert updated_category.description == "Updated description"

# @pytest.mark.asyncio
# async def test_delete_category(db_session: AsyncSession, new_category_data: CategoryCreate):
#     category = await CategoryService.create_category(db_session, new_category_data)
#     response = await CategoryService.delete_category(db_session, category.id)
#     assert response is True
#     deleted_category = await CategoryService.get_category(db_session, category.id)
#     assert deleted_category is None
