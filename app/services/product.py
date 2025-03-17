from sqlalchemy.future import select
from sqlalchemy import and_
from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import SQLAlchemyError
import logging
import json
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

 
    # all Products
    
    @staticmethod
    async def get_products(db: AsyncSession, user: User):
        await ProductService._verify_user_authorization(user)
        cache_key = f"user_products:{user.id}"
        
        try:
            cached_products = await redis_service.get(cache_key)
            if cached_products:
                logger.info(f"✅ Cache hit: {cache_key}")
                return [ProductResponse(**product) for product in json.loads(cached_products)]
        except Exception as e:
            logger.error(f"Redis error: {str(e)}")

        logger.info(f"❌ Cache miss: Fetching from DB - {cache_key}")
        try:
            result = await db.execute(select(Product).where(Product.user_id == user.id))
            products = result.scalars().all()
            product_responses = [ProductResponse.from_orm(p) for p in products]
            
            try:
                await redis_service.set(
                    cache_key,
                    json.dumps([p.model_dump() for p in product_responses]),
                    expire=300
                )
            except Exception as e:
                logger.error(f"Cache update failed: {str(e)}")
            
            return product_responses
        except SQLAlchemyError as e:
            logger.error(f"Database error: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Database operation failed"
            )

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
