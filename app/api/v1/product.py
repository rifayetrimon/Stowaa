from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.api import deps
from app.db.session import get_db
from app.schemas.product import ProductBase, ProductCreate, ProductUpdate, ProductResponse
from app.models.product import Product
from app.models.user import User
from sqlalchemy.future import select


router = APIRouter(
    prefix="/products",
    tags=["products"],
)



# create product endpoint
@router.post("/create", response_model=ProductCreate)
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