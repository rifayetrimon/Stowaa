# import pytest
# from httpx import AsyncClient
# from app.models.category import Category
# from app.schemas.category import CategoryCreate, CategoryUpdate
# from app.services.category import CategoryService

# @pytest.mark.asyncio
# async def test_create_category(async_client: AsyncClient, db_session, test_user):
#     category_data = {"name": "Test Category", "description": "A test category"}
#     response = await async_client.post("/category/create", json=category_data, headers={"Authorization": f"Bearer {test_user.token}"})
#     assert response.status_code == 200
#     data = response.json()
#     assert data["status"] == "success"
#     assert data["data"]["name"] == "Test Category"

# @pytest.mark.asyncio
# async def test_get_categories(async_client: AsyncClient, db_session, test_user):
#     response = await async_client.get("/category/", headers={"Authorization": f"Bearer {test_user.token}"})
#     assert response.status_code == 200
#     data = response.json()
#     assert data["status"] == "success"
#     assert isinstance(data["data"], list)

# @pytest.mark.asyncio
# async def test_get_category(async_client: AsyncClient, db_session, test_user, test_category):
#     response = await async_client.get(f"/category/{test_category.id}", headers={"Authorization": f"Bearer {test_user.token}"})
#     assert response.status_code == 200
#     data = response.json()
#     assert data["status"] == "success"
#     assert data["data"]["id"] == test_category.id

# @pytest.mark.asyncio
# async def test_update_category(async_client: AsyncClient, db_session, test_user, test_category):
#     update_data = {"name": "Updated Category", "description": "Updated description"}
#     response = await async_client.put(f"/category/{test_category.id}", json=update_data, headers={"Authorization": f"Bearer {test_user.token}"})
#     assert response.status_code == 200
#     data = response.json()
#     assert data["status"] == "success"
#     assert data["name"] == "Updated Category"

# @pytest.mark.asyncio
# async def test_delete_category(async_client: AsyncClient, db_session, test_user, test_category):
#     response = await async_client.delete(f"/category/{test_category.id}", headers={"Authorization": f"Bearer {test_user.token}"})
#     assert response.status_code == 200
#     data = response.json()
#     assert data["status"] == "success"

#     # Ensure category is deleted
#     response = await async_client.get(f"/category/{test_category.id}", headers={"Authorization": f"Bearer {test_user.token}"})
#     assert response.status_code == 404
