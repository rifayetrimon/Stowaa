from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from app.schemas.user import UserCreate, UserLogin, UserResponse, Token, UserRead, UserUpdate
from app.models.user import User
from app.db.session import get_db
from app.core.security import verify_password, create_access_token, hash_password
from sqlalchemy.future import select
from app.api.deps import get_current_user
from typing import Annotated
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from app.services.notification import NotificationService
from app.schemas.user import PromoNotificationSchema




router = APIRouter(
    prefix="/users",
    tags=["users"], 
)


         
# User Registration
@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def register_user(new_user: UserCreate, db: AsyncSession = Depends(get_db)):

    result_email = await db.execute(select(User).where(User.email == new_user.email)) # check if email already exists
    existing_user_email = result_email.scalar_one_or_none()

    if existing_user_email:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Email already registered!")

    result_phone_number = await db.execute(select(User).where(User.phone_number == new_user.phone_number)) # check if phone number already exists
    existing_user_phone = result_phone_number.scalar_one_or_none()

    if existing_user_phone:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Phone number already registered!")

    hashed_password = hash_password(new_user.password) # hash password

    new_user_model = User(
        email=new_user.email,
        hashed_password=hashed_password,
        name=new_user.name,
        phone_number=new_user.phone_number
    )

    db.add(new_user_model)
    await db.commit()
    await db.refresh(new_user_model)

    response = UserResponse(
        status = "success",
        message = "User registered successfully",
        data = UserRead.model_validate(new_user_model)
    )

    return response


# authenticate user 
async def authenticate_user(email: str, password: str, db: AsyncSession):
    result = await db.execute(select(User).where(User.email == email))
    user = result.scalars().first()

    if not user or not verify_password(password, user.hashed_password):
        return False

    return user 


# token for authenticate user 
@router.post("/token", response_model=Token)
async def login_for_access_token(form_data: Annotated[OAuth2PasswordRequestForm, Depends()], db: AsyncSession = Depends(get_db)):
    user = await authenticate_user(form_data.username, form_data.password, db)
    if not user:
        raise  HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Incorrect email or password combination!")

    token = create_access_token(data={"sub": user.email})
    return {"access_token": token, "token_type": "bearer"}


# User Login
@router.post("/login", response_model=Token)
async def login_user(user_in: UserLogin, db: AsyncSession = Depends(get_db)):
    user = await authenticate_user(user_in.email, user_in.password, db)
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Incorrect email or password combination!")

    token = create_access_token(data={"sub": user.email})
    return {"access_token": token, "token_type": "bearer"}


# get current user details
@router.get("/profile", response_model=UserResponse)
async def get_user_profile(current_user: User = Depends(get_current_user)):
    current_user_data = UserRead.model_validate(current_user)
    # return current_user_data

    response = {
        "status": "success", 
        "message": "User profile retrieved successfully", 
        "data": current_user_data  
    }

    return response



# Update user profile
@router.put("/profile-update", response_model=UserRead)
async def update_user_profile(user_in: UserUpdate, db: AsyncSession = Depends(get_db),current_user: User = Depends(get_current_user)):
    for key, value in user_in.model_dump(exclude_unset=True).items():
        setattr(current_user, key, value)
    db.add(current_user)
    await db.commit()
    return current_user




# Send promotional notifications
@router.post("/send-promo")
async def send_promo_notification(promo: PromoNotificationSchema,db: AsyncSession = Depends(get_db),current_user: User = Depends(get_current_user)):
    """
    Admin can send promotional notifications to all users.
    """
    # Ensure user is admin
    if current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Not authorized")

    # Get all users
    result = await db.execute(select(User))
    users = result.scalars().all()

    if not users:
        raise HTTPException(status_code=404, detail="No users found")

    # Send notification to each user
    for user in users:
        NotificationService.send_notification(
            user_email=user.email,
            subject=promo.subject,
            message=promo.message,
            method="email"
        )

    return {"status": "success", "message": "Promotional notifications sent"}



# logout 


