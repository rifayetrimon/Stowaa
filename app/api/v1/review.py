from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from app.schemas.review import ReviewCreate, ReviewResponse, ReviewCreateResponse, ReviewUpdate, ReviewUpdateResponse, ReviewUpdateData, ReviewListResponse
from app.models.review import Review
from app.db.session import get_db
from sqlalchemy.future import select
from app.models.user import User
from app.api.deps import get_current_user
from typing import Annotated


router = APIRouter(
    prefix="/reviews",
    tags=["reviews"], 
)


# Create a review
@router.post("/create", response_model=ReviewCreateResponse, status_code=status.HTTP_201_CREATED)
async def create_review(new_review: ReviewCreate, db: AsyncSession = Depends(get_db), current_user: Annotated[User, Depends(get_current_user)] = None):
    review = Review(**new_review.model_dump(), user_id=current_user.id)
    db.add(review)
    await db.commit()
    await db.refresh(review)

    response = {
        "status" : "success",
        "message" : "Review created successfully",
        "data" : ReviewResponse.model_validate(review)
    }
    
    return response



# Update a review
@router.put("/{review_id}", response_model=ReviewUpdateResponse)
async def update_review(review_id: int, review_data: ReviewUpdate, db: AsyncSession = Depends(get_db), current_user: Annotated[User, Depends(get_current_user)] = None):
    # Query the review using the review_id
    review = await db.execute(select(Review).where(Review.id == review_id))
    review = review.scalars().first()
    
    if not review:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Review not found")
    elif review.user_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="You are not authorized to update this review")
    
    # Update the review
    review.rating = review_data.rating
    review.comment = review_data.comment
    await db.commit()
    
    response = {
        "status" : "success",
        "message" : "Review updated successfully",
        "data" : ReviewUpdateData.model_validate(review)
    }
    
    return response



# Retrieve reviews for a product with product details
@router.get("/products/{product_id}", response_model=ReviewListResponse)
async def get_reviews_for_product(product_id: int, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Review).where(Review.product_id == product_id))
    reviews = result.scalars().all()
    
    return {
        "status": "success",
        "message": "Reviews retrieved successfully",
        "count": len(reviews),
        "data": [ReviewResponse.model_validate(review) for review in reviews]
    }


# delete a review
@router.delete("/{review_id}")
async def delete_review(review_id: int, db: AsyncSession = Depends(get_db), current_user: Annotated[User, Depends(get_current_user)] = None):
    # Query the review using the review_id
    review = await db.execute(select(Review).where(Review.id == review_id))
    review = review.scalars().first()
    
    if not review:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Review not found")
    elif review.user_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="You are not authorized to delete this review")
    
    db.delete(review)
    await db.commit()
    
    return {
        "status": "success",
        "message": "Review deleted successfully"
    }