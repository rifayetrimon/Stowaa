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
        """Create a new product with Redis cache invalidation."""
        await ProductService._verify_user_authorization(user)

        try:
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

            db.add(new_product)
            await db.commit()
            await db.refresh(new_product)

            # Invalidate relevant Redis caches
            logger.info(f"🔄 Invalidating Redis cache for user {user.id}")
            await redis_service.delete(f"user_products:{user.id}")
            
            # Convert to dictionary for consistent response
            product_dict = {
                column.name: getattr(new_product, column.name) 
                for column in new_product.__table__.columns
            }

            return product_dict

        except SQLAlchemyError as e:
            await db.rollback()
            logger.error(f"⚠️ Database error during product creation: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Database error during product creation"
            )

    @staticmethod
    async def get_products(db: AsyncSession, user: User):
        """Get all products with Redis caching."""
        await ProductService._verify_user_authorization(user)

        cache_key = f"user_products:{user.id}"
        logger.info(f"🔍 Attempting to get products for user {user.id}")
        logger.info(f"🔑 Cache key: {cache_key}")

        try:
            # Try to get from cache first
            cached_products = await redis_service.get(cache_key)
            if cached_products:
                logger.info(f"✅ Cache HIT! Found {len(cached_products)} products in Redis")
                return [ProductResponse(**product) for product in cached_products]
            logger.info("❌ Cache MISS! Fetching from database")

        except Exception as e:
            logger.error(f"⚠️ Redis error: {str(e)}")

        try:
            # Fetch from database
            result = await db.execute(
                select(Product).where(Product.user_id == user.id)
            )
            products = result.scalars().all()

            if not products:
                logger.info("📭 No products found in database")
                return []

            # Convert SQLAlchemy objects to dictionaries
            products_data = [
                {column.name: getattr(p, column.name) for column in p.__table__.columns}
                for p in products
            ]

            logger.info(f"📦 Found {len(products_data)} products in database")

            # Cache in Redis
            try:
                logger.info(f"💾 Caching {len(products_data)} products in Redis")
                await redis_service.set(cache_key, products_data, expire=300)
                logger.info("✅ Successfully cached in Redis")
            except Exception as e:
                logger.error(f"⚠️ Redis caching error: {str(e)}")

            return products_data

        except SQLAlchemyError as e:
            logger.error(f"⚠️ Database error: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Database error while fetching products"
            )

    @staticmethod
    async def get_product(db: AsyncSession, product_id: int, user: User):
        """Get a single product with Redis caching."""
        await ProductService._verify_user_authorization(user)

        cache_key = f"product:{product_id}"
        logger.info(f"🔍 Attempting to get product {product_id}")

        try:
            # Try cache first
            cached_product = await redis_service.get(cache_key)
            if cached_product:
                logger.info("✅ Cache HIT! Found product in Redis")
                return ProductResponse(**cached_product)
            logger.info("❌ Cache MISS! Fetching from database")

        except Exception as e:
            logger.error(f"⚠️ Redis error: {str(e)}")

        try:
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

            # Convert to dictionary
            product_dict = {
                column.name: getattr(product, column.name) 
                for column in product.__table__.columns
            }

            # Cache in Redis
            try:
                logger.info(f"💾 Caching product {product_id} in Redis")
                await redis_service.set(cache_key, product_dict, expire=300)
                logger.info("✅ Successfully cached in Redis")
            except Exception as e:
                logger.error(f"⚠️ Redis caching error: {str(e)}")

            return product_dict

        except SQLAlchemyError as e:
            logger.error(f"⚠️ Database error: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Database error while fetching product"
            )

    @staticmethod
    async def update_product(db: AsyncSession, product_id: int, product_data: ProductUpdate, user: User):
        """Update a product with Redis cache invalidation."""
        await ProductService._verify_user_authorization(user)

        try:
            # Get existing product
            product = await ProductService.get_product(db, product_id, user)
            if not product:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Product not found"
                )

            update_data = product_data.model_dump(exclude_unset=True)

            # SKU uniqueness check if SKU is being updated
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

            # Get product instance from database
            db_product = await db.get(Product, product_id)
            
            # Update fields
            for key, value in update_data.items():
                setattr(db_product, key, value)

            await db.commit()
            await db.refresh(db_product)

            # Invalidate Redis caches
            logger.info(f"🔄 Invalidating Redis caches for product {product_id}")
            await redis_service.delete(f"product:{product_id}")
            await redis_service.delete(f"user_products:{user.id}")

            # Convert to dictionary for response
            updated_dict = {
                column.name: getattr(db_product, column.name) 
                for column in db_product.__table__.columns
            }

            return updated_dict

        except SQLAlchemyError as e:
            await db.rollback()
            logger.error(f"⚠️ Database error during update: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Database error during update"
            )

    @staticmethod
    async def delete_product(db: AsyncSession, product_id: int, user: User):
        """Delete a product with Redis cache invalidation."""
        await ProductService._verify_user_authorization(user)

        try:
            # Get product first to verify ownership
            product = await ProductService.get_product(db, product_id, user)
            if not product:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Product not found"
                )

            # Get database instance
            db_product = await db.get(Product, product_id)
            await db.delete(db_product)
            await db.commit()

            # Invalidate Redis caches
            logger.info(f"🔄 Invalidating Redis caches for product {product_id}")
            await redis_service.delete(f"product:{product_id}")
            await redis_service.delete(f"user_products:{user.id}")

            return {"status": "success", "message": "Product deleted successfully"}

        except SQLAlchemyError as e:
            await db.rollback()
            logger.error(f"⚠️ Database error during deletion: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Database error during deletion"
            )