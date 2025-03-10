from sqlalchemy.future import select
from sqlalchemy import and_
from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import SQLAlchemyError
import logging
from app.models.product import Product
from app.models.user import User
from app.schemas.product import ProductCreate, ProductUpdate, ProductResponse
from app.services.redis_service import redis_service

logger = logging.getLogger(__name__)

class ProductService:
    
    @staticmethod
    async def _verify_user_authorization(user: User):
        if user.role.value not in ["admin", "seller"]:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You are not authorized to perform this action"
            )

    @staticmethod
    async def create_product(db: AsyncSession, product_data: ProductCreate, user: User):
        await ProductService._verify_user_authorization(user)

        # Check for existing SKU
        existing_product = await db.execute(
            select(Product).where(Product.sku == product_data.sku)
        )
        if existing_product.scalar():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="SKU already exists"
            )

        new_product = Product(
            **product_data.model_dump(exclude={"user_id"}),
            user_id=user.id
        )

        try:
            db.add(new_product)
            await db.commit()
            await db.refresh(new_product)

            # Invalidate cache
            await redis_service.delete(f"user_products:{user.id}")

            return new_product
        except SQLAlchemyError as e:
            await db.rollback()
            logger.error(f"Database error: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Database error"
            )


@staticmethod
async def get_products(db: AsyncSession, user: User):
    await ProductService._verify_user_authorization(user)

    cache_key = f"user_products:{user.id}"
    logger.info(f"🔍 Attempting to get products for user {user.id}")
    logger.info(f"🔑 Cache key: {cache_key}")

    try:
        cached_products = await redis_service.get(cache_key)
        if cached_products:
            logger.info(f"✅ Cache HIT! Found {len(cached_products)} products in Redis")
            return [ProductResponse(**product) for product in cached_products]
        else:
            logger.info("❌ Cache MISS! No data in Redis")
    except Exception as e:
        logger.error(f"⚠️ Redis get error: {str(e)}")

    # Get from database
    logger.info("📊 Fetching from database...")
    result = await db.execute(
        select(Product).where(Product.user_id == user.id)
    )
    products = result.scalars().all()
    
    if not products:
        logger.info("📭 No products found in database")
        return []

    # Convert SQLAlchemy objects to dictionaries
    try:
        products_data = []
        for p in products:
            product_dict = {
                column.name: getattr(p, column.name) 
                for column in p.__table__.columns
            }
            products_data.append(product_dict)
        
        logger.info(f"📦 Found {len(products_data)} products in database")
        
        # Try to cache in Redis
        logger.info(f"💾 Attempting to cache {len(products_data)} products in Redis")
        await redis_service.set(cache_key, products_data, expire=300)
        logger.info("✅ Successfully cached in Redis")
        
    except Exception as e:
        logger.error(f"⚠️ Error during caching: {str(e)}")

    return products


    # @staticmethod
    # async def get_products(db: AsyncSession, user: User):
    #     await ProductService._verify_user_authorization(user)

    #     cache_key = f"user_products:{user.id}"
    #     cached_products = await redis_service.get(cache_key)

    #     if cached_products:
    #         return [ProductResponse(**product) for product in cached_products]

    #     result = await db.execute(
    #         select(Product).where(Product.user_id == user.id)
    #     )
    #     products = result.scalars().all()

    #     if not products:
    #         return []

    #     # Store in Redis
    #     await redis_service.set(cache_key, products, expire=300)

    #     return products

    @staticmethod
    async def get_product(db: AsyncSession, product_id: int, user: User):
        await ProductService._verify_user_authorization(user)

        cache_key = f"product:{product_id}"
        cached_product = await redis_service.get(cache_key)

        if cached_product:
            return ProductResponse(**cached_product)

        result = await db.execute(
            select(Product).where(
                and_(
                    Product.id == product_id,
                    Product.user_id == user.id
                )
            )
        )
        product = result.scalar()
        if not product:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Product not found"
            )

        # Cache the product
        await redis_service.set(cache_key, product, expire=300)

        return product

    @staticmethod
    async def update_product(db: AsyncSession, product_id: int, product_data: ProductUpdate, user: User):
        await ProductService._verify_user_authorization(user)

        product = await ProductService.get_product(db, product_id, user)
        update_data = product_data.model_dump(exclude_unset=True)

        # SKU uniqueness check
        if 'sku' in update_data:
            existing = await db.execute(
                select(Product).where(
                    and_(
                        Product.sku == update_data['sku'],
                        Product.id != product_id
                    )
                )
            )
            if existing.scalar():
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="SKU already exists"
                )

        # Update fields
        for key, value in update_data.items():
            setattr(product, key, value)

        try:
            await db.commit()
            await db.refresh(product)

            # Invalidate cache
            await redis_service.delete(f"product:{product_id}")
            await redis_service.delete(f"user_products:{user.id}")

            return product
        except SQLAlchemyError as e:
            await db.rollback()
            logger.error(f"Database Update Error: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Update failed due to database error"
            )

    @staticmethod
    async def delete_product(db: AsyncSession, product_id: int, user: User):
        await ProductService._verify_user_authorization(user)

        product = await ProductService.get_product(db, product_id, user)

        try:
            await db.delete(product)
            await db.commit()

            # Invalidate cache
            await redis_service.delete(f"product:{product_id}")
            await redis_service.delete(f"user_products:{user.id}")

        except SQLAlchemyError as e:
            await db.rollback()
            logger.error(f"Deletion failed: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Deletion failed"
            )



@router.get("/redis-debug")
async def redis_debug():
    """Debug Redis connection and data"""
    try:
        # Test basic connection
        await redis_service._ensure_connection()
        if redis_service._redis is None:
            return {"status": "error", "message": "Could not connect to Redis"}

        # Test setting data
        test_key = "debug_test"
        test_data = {"test": "data"}
        await redis_service.set(test_key, test_data, expire=60)

        # Test getting data
        retrieved_data = await redis_service.get(test_key)

        # Get all keys
        all_keys = await redis_service._redis.keys("*")

        return {
            "status": "success",
            "connection": "active",
            "test_write": test_data,
            "test_read": retrieved_data,
            "all_keys_in_redis": all_keys,
            "redis_info": await redis_service._redis.info()
        }
    except Exception as e:
        return {
            "status": "error",
            "message": str(e)
        }