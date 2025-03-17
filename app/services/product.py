from sqlalchemy.future import select
from sqlalchemy.orm import selectinload
from sqlalchemy import and_
from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import SQLAlchemyError
import logging

from app.models.product import Product
from app.models.user import User
from app.schemas.product import ProductCreate, ProductUpdate

logger = logging.getLogger(__name__)

class ProductService:

    @staticmethod
    async def _verify_user_authorization(user: User):
        if user.role.value not in ["admin", "seller"]:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Operation not permitted for current role"
            )

    @staticmethod
    async def create_product(db: AsyncSession, product_data: ProductCreate, user: User):
        try:
            await ProductService._verify_user_authorization(user)

            # Check for existing SKU within user's products
            existing = await db.execute(
                select(Product)
                .where(and_(
                    Product.sku == product_data.sku,
                    Product.user_id == user.id
                ))
            )
            if existing.scalar():
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="SKU must be unique within your products"
                )

            new_product = Product(
                **product_data.model_dump(exclude={"user_id"}),
                user_id=user.id
            )

            db.add(new_product)
            await db.commit()
            await db.refresh(new_product)
            return new_product

        except HTTPException:
            raise
        except Exception as e:
            await db.rollback()
            logger.error(f"Product creation failed: {str(e)}", exc_info=True)
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Product creation failed"
            )

    @staticmethod
    async def get_products(db: AsyncSession, user: User):
        try:
            await ProductService._verify_user_authorization(user)
            
            query = select(Product).options(selectinload(Product.user))
            if user.role.value == "seller":
                query = query.where(Product.user_id == user.id)

            result = await db.execute(query)
            return result.scalars().all()

        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Product retrieval failed: {str(e)}", exc_info=True)
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to retrieve products"
            )

    @staticmethod
    async def get_product(db: AsyncSession, product_id: int, user: User):
        try:
            await ProductService._verify_user_authorization(user)

            query = select(Product)\
                .options(selectinload(Product.user))\
                .where(Product.id == product_id)
            
            if user.role.value == "seller":
                query = query.where(Product.user_id == user.id)

            result = await db.execute(query)
            product = result.scalar()
            
            if not product:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Product not found"
                )
            return product

        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Product fetch failed: {str(e)}", exc_info=True)
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to fetch product"
            )

    @staticmethod
    async def update_product(db: AsyncSession, product_id: int, product_data: ProductUpdate, user: User):
        try:
            product = await ProductService.get_product(db, product_id, user)
            update_dict = product_data.model_dump(exclude_unset=True)

            if 'sku' in update_dict:
                existing = await db.execute(
                    select(Product).where(and_(
                        Product.sku == update_dict['sku'],
                        Product.user_id == product.user_id,
                        Product.id != product_id
                    ))
                )
                if existing.scalar():
                    raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail="SKU already exists for your products"
                    )

            for key, value in update_dict.items():
                setattr(product, key, value)

            await db.commit()
            await db.refresh(product, ['user'])  # Explicitly reload relationships
            return product

        except HTTPException:
            raise
        except Exception as e:
            await db.rollback()
            logger.error(f"Product update failed: {str(e)}", exc_info=True)
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Product update failed"
            )

    @staticmethod
    async def delete_product(db: AsyncSession, product_id: int, user: User):
        try:
            product = await ProductService.get_product(db, product_id, user)
            await db.delete(product)
            await db.commit()
        except HTTPException:
            raise
        except Exception as e:
            await db.rollback()
            logger.error(f"Product deletion failed: {str(e)}", exc_info=True)
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Product deletion failed"
            )