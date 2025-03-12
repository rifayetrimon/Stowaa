from fastapi import APIRouter, Depends, HTTPException, status
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





