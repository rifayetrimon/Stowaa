from sqlalchemy.future import select
from sqlalchemy.orm import selectinload
from sqlalchemy import and_
from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import SQLAlchemyError
import logging

from app.models.product import Product
from app.models.user import User
from app.schemas.product import ProductCreate, ProductUpdate, ProductResponse

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

        # Check SKU uniqueness for the current user's products
        existing_product = await db.execute(
            select(Product).where(
                and_(
                    Product.sku == product_data.sku,
                    Product.user_id == user.id
                )
            )
        )
        if existing_product.scalar():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="SKU already exists for your account"
            )

        new_product = Product(
            **product_data.model_dump(exclude={"user_id"}),
            user_id=user.id
        )

        try:
            db.add(new_product)
            await db.commit()
            await db.refresh(new_product)
            return new_product
        except SQLAlchemyError as e:
            await db.rollback()
            logger.error(f"Database error: {str(e)}", exc_info=True)
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Database error"
            )

    @staticmethod
    async def get_products(db: AsyncSession, user: User):
        await ProductService._verify_user_authorization(user)
        
        query = select(Product)
        if user.role.value == "seller":
            query = query.where(Product.user_id == user.id)
        
        result = await db.execute(query)
        products = result.scalars().all()
        return products

    @staticmethod
    async def get_product(db: AsyncSession, product_id: int, user: User):
        await ProductService._verify_user_authorization(user)

        query = select(Product).where(Product.id == product_id)
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

    @staticmethod
    async def update_product(db: AsyncSession, product_id: int, product_data: ProductUpdate, user: User):
        await ProductService._verify_user_authorization(user)

        product = await ProductService.get_product(db, product_id, user)
        update_data = product_data.model_dump(exclude_unset=True)

        if 'sku' in update_data:
            # Check SKU uniqueness against the original owner's products
            existing = await db.execute(
                select(Product).where(
                    and_(
                        Product.sku == update_data['sku'],
                        Product.user_id == product.user_id,
                        Product.id != product_id
                    )
                )
            )
            if existing.scalar():
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="SKU already exists for this product's owner"
                )

        for key, value in update_data.items():
            setattr(product, key, value)

        try:
            await db.commit()
            await db.refresh(product)
            return product
        except SQLAlchemyError as e:
            await db.rollback()
            logger.error(f"Database Update Error: {str(e)}", exc_info=True)
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
        except SQLAlchemyError as e:
            await db.rollback()
            logger.error(f"Deletion failed: {str(e)}", exc_info=True)
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Deletion failed"
            )