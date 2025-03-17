from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
import logging

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
logger = logging.getLogger(__name__)

@router.post("/create", response_model=ProductCreateResponse)
async def create_product(
    product_data: ProductCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """API endpoint to create a new product."""
    product_dict = await ProductService.create_product(db, product_data, current_user)

    # Ensure Pydantic model validation
    product_response = ProductResponse(**product_dict)

    return ProductCreateResponse(
        status="success",
        message="Product successfully created",
        data=product_response
    )


@router.get("/", response_model=ProductListResponse)
async def get_products(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    products = await ProductService.get_products(db, current_user)
    return ProductListResponse(
        status="success",
        message="Products successfully retrieved",
        count=len(products),
        data=products
    )

@router.get("/{product_id}", response_model=ProductDetailsResponse)
async def get_product(
    product_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    product = await ProductService.get_product(db, product_id, current_user)
    return ProductDetailsResponse(
        status="success",
        message="Product successfully retrieved",
        data=ProductResponse.model_validate(product)
    )

@router.put("/{product_id}", response_model=ProductDetailsResponse)
async def update_product(
    product_id: int,
    product_data: ProductUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    updated_product = await ProductService.update_product(db, product_id, product_data, current_user)
    return ProductDetailsResponse(
        status="success",
        message="Product successfully updated",
        data=ProductResponse.model_validate(updated_product)
    )

@router.delete("/{product_id}")
async def delete_product(
    product_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    await ProductService.delete_product(db, product_id, current_user)
    return {"status": "success", "message": "Product successfully deleted"}
