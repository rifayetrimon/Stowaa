import datetime
import logging
from sqlalchemy.future import select
from sqlalchemy.orm import selectinload
from sqlalchemy import and_
from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import SQLAlchemyError

from app.models.product import Product
from app.models.user import User
from app.schemas.category import CategoryResponse
from app.schemas.product import ProductCreate, ProductResponse, ProductUpdate

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

            # Check for existing SKU within the user's products
            existing = await db.execute(
                select(Product).where(
                    and_(Product.sku == product_data.sku, Product.user_id == user.id)
                )
            )
            if existing.scalar():
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="SKU must be unique within your products"
                )

            new_product = Product(
                **product_data.model_dump(exclude={"user_id"}),
                user_id=user.id  # Assign the current user as the owner
            )

            db.add(new_product)
            await db.commit()
            await db.refresh(new_product)

            # Ensure proper serialization
            return ProductResponse(
                id=new_product.id,
                user_id=new_product.user_id,
                name=new_product.name,
                description=new_product.description,
                price=new_product.price,
                category_id=new_product.category_id,
                stock_quantity=new_product.stock_quantity,
                sku=new_product.sku,
                image_url=new_product.image_url,
                is_active=new_product.is_active,
                updated_at=new_product.updated_at
            )

        except HTTPException:
            raise
        except Exception as e:
            await db.rollback()
            logger.error(f"Product creation failed: {str(e)}", exc_info=True)
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Product creation failed: {str(e)}"
            )


    @staticmethod
    async def get_products(db: AsyncSession, user: User):
        try:
            await ProductService._verify_user_authorization(user)

            query = select(Product).options(selectinload(Product.category))
            if user.role.value == "seller":
                query = query.where(Product.user_id == user.id)

            result = await db.execute(query)
            products = result.scalars().all()

            # Debugging: Log product data
            logger.info(f"Retrieved {len(products)} products.")

            # Convert to Pydantic response format
            product_list = []
            for p in products:
                product_list.append(ProductResponse(
                    id=p.id,
                    name=p.name,
                    description=p.description,
                    price=p.price,
                    category_id=p.category_id,
                    category=CategoryResponse(id=p.category.id, name=p.category.name) if p.category else None,
                    stock_quantity=p.stock_quantity,
                    sku=p.sku,
                    image_url=str(p.image_url) if p.image_url else None,
                    is_active=p.is_active,
                    user_id=p.user_id,
                    updated_at=p.updated_at
                ))

            return product_list

        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Product retrieval failed: {str(e)}", exc_info=True)
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to retrieve products: {str(e)}"  # Now includes the actual error message
            )


    @staticmethod
    async def get_product(db: AsyncSession, product_id: int, user: User):
        try:
            await ProductService._verify_user_authorization(user)

            query = select(Product).options(selectinload(Product.category)).where(Product.id == product_id)
            
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
            await db.refresh(product, ['category'])
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
            return {"message": "Product deleted successfully"}

        except HTTPException:
            raise
        except Exception as e:
            await db.rollback()
            logger.error(f"Product deletion failed: {str(e)}", exc_info=True)
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Product deletion failed"
            )
