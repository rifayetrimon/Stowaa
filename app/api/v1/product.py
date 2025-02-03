from datetime import datetime
from sqlite3 import IntegrityError
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from app.api import deps
from app.db.session import get_db
from app.schemas.product import ProductCreate, ProductUpdate, ProductResponse, ProductListResponse, ProductCreateResponse, ProductDetailsResponse
from app.models.product import Product
from app.models.user import User
from sqlalchemy.future import select



router = APIRouter(
    prefix="/products",
    tags=["products"],
)



# create product endpoint
@router.post("/create", response_model=ProductCreateResponse)
async def create_product(product_in: ProductCreate, db: AsyncSession = Depends(get_db), current_user: User = Depends(deps.get_current_user)):
    
    if not current_user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="You are not authenticated!")
    elif current_user.role.value not in ["admin", "seller"]:  
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="You are not authorized to create a product")
    
    new_product = Product(
        **product_in.model_dump(exclude_unset=True),
        user_id=current_user.id
    )
 
    try:
        db.add(new_product)
        await db.commit()
        await db.refresh(new_product)
    except IntegrityError as e:
        await db.rollback()
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    
    response = {
        "status" : "success",
        "message" : "Product created successfully",
        "data" : ProductResponse.model_validate(new_product)
    }

    return response



# get all products endpoint
@router.get("/", response_model=ProductListResponse)
async def get_all_products(db: AsyncSession = Depends(get_db), current_user: User = Depends(deps.get_current_user)):
    result = await db.execute(select(Product).where(Product.user_id == current_user.id))
    products = result.scalars().all()

    return {
        "status": "success",
        "message": "Products retrieved successfully",
        "count": len(products),
        "data": [ProductResponse.model_validate(product) for product in products]
    }



# product details 
@router.get("/{product_id}", response_model=ProductDetailsResponse)
async def get_product(product_id: int, db: AsyncSession = Depends(get_db), current_user: User = Depends(deps.get_current_user)):
    product = await db.execute(select(Product).where(Product.id == product_id and Product.user_id == current_user.id))
    product = product.scalar()
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    
    response = {
        "status" : "success",
        "message" : "Product get successfully",
        "data" : ProductResponse.model_validate(product)
    }

    return response



# update product 
@router.put("/{product_id}", response_model=ProductResponse)
async def update_product(product_id: int, product_in: ProductUpdate, db: AsyncSession = Depends(get_db), current_user: User = Depends(deps.get_current_user)):
    product = await db.execute(select(Product).where(Product.id == product_id and Product.user_id == current_user.id))
    product = product.scalar()
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")

    try:
        update_data = product_in.model_dump(exclude_unset=True)

        for key, value in update_data.items():
            setattr(product, key, value)
        
        product.updated_at = datetime.now()
        await db.commit()
        await db.refresh(product)
        
    except Exception as e:
        await db.rollback()
        raise HTTPException(status_code=400, detail=str(e))

    return ProductResponse.model_validate(product)


# delete product
@router.delete("/{product_id}")
async def delete_product(product_id: int, db: AsyncSession = Depends(get_db), current_user: User = Depends(deps.get_current_user)):
    product = await db.execute(
        select(Product).where(
            (Product.id == product_id) & (Product.user_id == current_user.id)
        )
    )
    product = product.scalar()
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")

    try:
        await db.delete(product)
        await db.commit()
    except Exception as e:
        await db.rollback()
        raise HTTPException(status_code=400, detail=str(e))

    return {"message": "Product deleted successfully!"}