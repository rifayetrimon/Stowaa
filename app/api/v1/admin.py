from datetime import datetime, timedelta
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import func
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.user import User
from app.schemas.admin import AllSellersResponse, SellerResponse, ChangeUserRoleRequest, AllUserResponse, UserResponse
from app.db.session import get_db
from sqlalchemy.future import select
from app.models.user import User, UserRole
from app.api import deps
from app.models.user import User




router = APIRouter(
    prefix="/admin",
    tags=["admin"],
)



# get all sellers
@router.get("/sellers", response_model=AllSellersResponse)
async def get_sellers(db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(User).where(User.role == "seller"))
    sellers = result.scalars().all()

    return {
        "status": "success",
        "message": "Sellers retrieved successfully",
        "count": len(sellers),
        "data": [SellerResponse.model_validate(item) for item in sellers]
    }



# get all user
@router.get("/allusers", response_model=AllUserResponse)
async def get_users(db: AsyncSession = Depends(get_db),current_user: User = Depends(deps.get_current_user)):
    if current_user.role != UserRole.ADMIN:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, 
            detail="Only admins can view all users"
        )

    result = await db.execute(select(User).where(User.role != UserRole.ADMIN))
    users = result.scalars().all()

    return {
        "status": "success",
        "message": "Users retrieved successfully",
        "count": len(users),
        "data": [UserResponse.model_validate(item) for item in users]
    }




# chnage user role
@router.put("/users/{user_id}/role", response_model=dict)
async def change_user_role(user_id: int,request: ChangeUserRoleRequest,db: AsyncSession = Depends(get_db),current_user: User = Depends(deps.get_current_user)):

    # ✅ Step 1: Ensure the current user is an admin
    if current_user.role != UserRole.ADMIN:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, 
            detail="Only admins can change user roles"
        )

    # ✅ Step 2: Fetch the target user from the database
    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalars().first()

    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

    # ✅ Step 3: Prevent changing another admin's role (except self-modification)
    if user.role == UserRole.ADMIN and current_user.id != user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, 
            detail="You cannot change another admin's role"
        )

    # ✅ Step 4: Update the user's role
    user.role = request.role
    await db.commit()
    await db.refresh(user)

    return {"status": "success", "message": f"User role updated to {user.role}"}





@router.get("/users/count", response_model=dict)
async def get_users_current_year(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(deps.get_current_user)
):
    if current_user.role != UserRole.ADMIN:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only admins can view user counts"
        )

    current_year = datetime.now().year
    start_of_year = datetime(current_year, 1, 1)
    end_of_year = datetime(current_year, 12, 31, 23, 59, 59)

    last_year = current_year - 1
    start_of_last_year = datetime(last_year, 1, 1)
    end_of_last_year = datetime(last_year, 12, 31, 23, 59, 59)

    try:
        # Current year count
        stmt_current = select(func.count()).select_from(User).where(
            User.created_at.isnot(None),
            User.created_at >= start_of_year,
            User.created_at <= end_of_year,
            User.role != UserRole.ADMIN
        )
        result_current = await db.execute(stmt_current)
        user_count_current = result_current.scalar_one()

        # Last year count
        stmt_last = select(func.count()).select_from(User).where(
            User.created_at.isnot(None),
            User.created_at >= start_of_last_year,
            User.created_at <= end_of_last_year,
            User.role != UserRole.ADMIN
        )
        result_last = await db.execute(stmt_last)
        user_count_last = result_last.scalar_one()

        # Calculate percentage change
        if user_count_last == 0:
            percentage_change = None
        else:
            change = ((user_count_current - user_count_last) / user_count_last) * 100
            percentage_change = f"{change:+.2f}%"

        return {
            "status": "success",
            "message": f"Total users registered in {current_year}",
            "total_users": user_count_current,
            "percentage_change_from_last_year": percentage_change or "N/A"
        }

    except Exception as e:
        print(f"Error occurred: {e}")
        raise HTTPException(status_code=500, detail=f"Internal Server Error: {str(e)}")


