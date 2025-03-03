from datetime import datetime
from sqlite3 import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from fastapi import HTTPException, status
from app.models.product import Product
from app.schemas.product import ProductCreate, ProductUpdate, ProductResponse
from app.services.redis_service import redis_service


# Cache keys
def get_cache_key_product_list(user_id: int):
    return f"user:{user_id}:products"

def get_cache_key_product(product_id: int):
    return f"product:{product_id}"


# Get all products with caching
async def get_products(db: AsyncSession, user_id: int):
    cache_key = get_cache_key_product_list(user_id)
    cached_products = await redis_service.get(cache_key)

    if cached_products:
        return cached_products

    result = await db.execute(select(Product).where(Product.user_id == user_id))
    products = result.scalars().all()

    product_responses = [ProductResponse.model_validate(product).model_dump() for product in products]

    await redis_service.set(cache_key, product_responses)
    return product_responses


# Get a single product with caching
async def get_product(db: AsyncSession, user_id: int, product_id: int):
    cache_key = get_cache_key_product(product_id)
    cached_product = await redis_service.get(cache_key)

    if cached_product:
        return cached_product

    product = await db.execute(select(Product).where(
        (Product.id == product_id) & (Product.user_id == user_id)
    ))
    product = product.scalar()

    if not product:
        raise HTTPException(status_code=404, detail="Product not found")

    product_response = ProductResponse.model_validate(product).model_dump()

    await redis_service.set(cache_key, product_response)
    return product_response


# Create a new product

async def create_product(db: AsyncSession, user_id: int, product_in: ProductCreate):
    try:
        product_data = product_in.model_dump()
        
        # Check for duplicate SKU
        existing_sku = await db.execute(
            select(Product).where(Product.sku == product_data['sku'])
        )
        if existing_sku.scalar():
            raise HTTPException(
                status_code=400,
                detail="SKU already exists"
            )

        new_product = Product(
            **product_data,
            user_id=user_id  # Set from parameter
        )

        db.add(new_product)
        await db.commit()
        await db.refresh(new_product)

        await redis_service.delete(get_cache_key_product_list(user_id))

        return ProductResponse.model_validate(new_product)
        
    except IntegrityError as e:
        await db.rollback()
        raise HTTPException(
            status_code=400,
            detail="Database integrity error: " + str(e)
        )


# Update an existing product
async def update_product(db: AsyncSession, user_id: int, product_id: int, product_in: ProductUpdate):
    product = await db.execute(select(Product).where(
        (Product.id == product_id) & (Product.user_id == user_id)
    ))
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

        await redis_service.delete(get_cache_key_product(product_id))
        await redis_service.delete(get_cache_key_product_list(user_id))

        return ProductResponse.model_validate(product)
    except Exception as e:
        await db.rollback()
        raise HTTPException(status_code=400, detail=str(e))


# Delete a product
async def delete_product(db: AsyncSession, user_id: int, product_id: int):
    product = await db.execute(select(Product).where(
        (Product.id == product_id) & (Product.user_id == user_id)
    ))
    product = product.scalar()

    if not product:
        raise HTTPException(status_code=404, detail="Product not found")

    try:
        await db.delete(product)
        await db.commit()

        await redis_service.delete(get_cache_key_product(product_id))
        await redis_service.delete(get_cache_key_product_list(user_id))

        return {"message": "Product deleted successfully!"}
    except Exception as e:
        await db.rollback()
        raise HTTPException(status_code=400, detail=str(e))
