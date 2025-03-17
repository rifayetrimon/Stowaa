from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.session import get_db
from app.schemas.product import (
    ProductCreate,
    ProductUpdate,
    ProductResponse,
    ProductListResponse,
    ProductCreateResponse,
    ProductDetailsResponse
)
from app.models.user import User
from app.api.deps import get_current_user
from app.services.product import ProductService

router = APIRouter(prefix="/products", tags=["products"])

@router.post("/create", response_model=ProductCreateResponse)
async def create_product(
    create_product: ProductCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Create a new product."""
    new_product = await ProductService.create_product(db, create_product, current_user)
    product_dict = {column.name: getattr(new_product, column.name) for column in new_product.__table__.columns}
    return ProductCreateResponse(status="success", message="Product created successfully", data=ProductResponse.model_validate(product_dict))

@router.get("/", response_model=ProductListResponse)
async def get_all_products(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Retrieve all products."""
    products = await ProductService.get_products(db, current_user)
    return ProductListResponse(status="success", message="Products retrieved successfully", count=len(products), data=products)

@router.put("/{product_id}", response_model=ProductDetailsResponse)
async def update_product(
    product_id: int,
    product_update: ProductUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Update a product"""
    updated_product = await ProductService.update_product(db, product_id, product_update, current_user)
    product_dict = {column.name: getattr(updated_product, column.name) for column in updated_product.__table__.columns}
    return ProductDetailsResponse(status="success", message="Product updated successfully", data=ProductResponse.model_validate(product_dict))

@router.delete("/{product_id}")
async def delete_product(
    product_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Delete a product."""
    await ProductService.delete_product(db, product_id, current_user)
    return {"status": "success", "message": "Product deleted successfully"}
