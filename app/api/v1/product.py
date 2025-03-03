from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from app.services.product import (
    get_products, get_product, create_product, update_product, delete_product
)
from app.schemas.product import ProductCreate, ProductUpdate, ProductResponse, ProductListResponse, ProductCreateResponse, ProductDetailsResponse
from app.db.session import get_db
from app.models.user import User
from app.api.deps import get_current_user

router = APIRouter(prefix="/products", tags=["products"])


@router.get("/", response_model=ProductListResponse)
async def list_products(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    products = await get_products(db, current_user.id)
    return {"status": "success", "message": "Products retrieved successfully", "count": len(products), "data": products}


@router.get("/{product_id}", response_model=ProductDetailsResponse)
async def retrieve_product(
    product_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    product = await get_product(db, current_user.id, product_id)
    return {"status": "success", "message": "Product retrieved successfully", "data": product}


@router.post("/create", response_model=ProductCreateResponse)
async def add_product(
    product_in: ProductCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    if current_user.role.value not in ["admin", "seller"]:
        raise HTTPException(status_code=403, detail="Not authorized")

    product = await create_product(db, current_user.id, product_in)
    return ProductCreateResponse(
        status="success",
        message="Product created successfully",
        data=product
    )


@router.put("/{product_id}", response_model=ProductResponse)
async def modify_product(
    product_id: int,
    product_in: ProductUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    product = await update_product(db, current_user.id, product_id, product_in)
    return product


@router.delete("/{product_id}")
async def remove_product(
    product_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    return await delete_product(db, current_user.id, product_id)
