from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.api import deps
from app.db.session import get_db
from app.schemas.product import ProductCreate, ProductUpdate, ProductResponse
from app.models.product import Product
from app.models.user import User
from sqlalchemy.future import select


router = APIRouter(
    prefix="/products",
    tags=["products"],
)



# create product endpoint
@router.post("/create", response_model=ProductResponse)
async def create_product(product_in: ProductCreate, db: Session = Depends(get_db), current_user: User = Depends(deps.get_current_user)):
    if not current_user:
        raise HTTPException(status_code=401, detail="You are not authenticated!")
    
    new_product = Product(
        **product_in.model_dump(),
        user_id=current_user.id
    )

    try:
        db.add(new_product)
        await db.commit()
        await db.refresh(new_product)
    except Exception as e:
        await db.rollback()
        raise HTTPException(status_code=400, detail=str(e))

    return new_product



# get all products endpoint
@router.get("/", response_model=list[ProductResponse])
async def get_all_products(db: Session = Depends(get_db), current_user: User = Depends(deps.get_current_user)):
    result = await db.execute(select(Product).where(Product.user_id == current_user.id))
    products = result.scalars().all()
    return products     



# product details 
@router.get("/{product_id}", response_model=ProductResponse)
async def get_product(product_id: int, db: Session = Depends(get_db), current_user: User = Depends(deps.get_current_user)):
    product = await db.execute(select(Product).where(Product.id == product_id and Product.user_id == current_user.id))
    product = product.scalar()
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    return product



# update product 
@router.put("/{product_id}", response_model=ProductUpdate)
async def update_product(product_id: int, product_in: ProductUpdate, db: Session = Depends(get_db), current_user: User = Depends(deps.get_current_user)):
    product = await db.execute(select(Product).where(Product.id == product_id and Product.user_id == current_user.id))
    product = product.scalar()
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")

    try:
        for key, value in product_in.model_dump().items():
            setattr(product, key, value)
        await db.commit()
        await db.refresh(product)
    except Exception as e:
        await db.rollback()
        raise HTTPException(status_code=400, detail=str(e))

    return product


# delete product
@router.delete("/{product_id}")
async def delete_product(product_id: int, db: Session = Depends(get_db), current_user: User = Depends(deps.get_current_user)):
    product = await db.execute(select(Product).where(Product.id == product_id and Product.user_id == current_user.id))
    product = product.scalar()
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")

    try:
        db.delete(product)
        await db.commit()
    except Exception as e:
        await db.rollback()
        raise HTTPException(status_code=400, detail=str(e))

    return {"message": "Product deleted successfully!"}