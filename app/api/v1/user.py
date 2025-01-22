from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from app.schemas.user import UserCreate, UserLogin, UserResponse, Token, UserRead, UserUpdate
from app.models.user import User
from app.db.session import get_db
from app.core.security import verify_password, create_access_token, hash_password
from sqlalchemy.future import select
from app.api.deps import get_current_user


router = APIRouter()


# User Regisration
@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def register_user(user_in: UserCreate, db: AsyncSession = Depends(get_db)):
    existing_user = await db.execute(
        User.__table__.select().where(User.email == user_in.email)
    )

    if existing_user.scalar():
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="User already registered by this email!")
    
    new_hased_password = hash_password(user_in.password)    

    new_user = User(
        name=user_in.name,
        email=user_in.email,
        hashed_password=new_hased_password
    )

    db.add(new_user)
    await db.commit()
    return new_user



# User Login
@router.post("/login", response_model=Token)
async def login_user(user_in: UserLogin, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(User).where(User.email == user_in.email))
    user = result.scalars().first()

    if not user or not verify_password(user_in.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password combination!",
        )

    token = create_access_token(data={"sub": user.email})

    return {"access_token": token, "token_type": "bearer"}


# Get current user
@router.get("/profile", response_model=UserRead)
async def get_user_profile(current_user: User = Depends(get_current_user)):
    return current_user



# Update user profile
@router.put("/profile-update", response_model=UserRead)
async def update_user_profile(
    user_in: UserUpdate, 
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    for key, value in user_in.dict(exclude_unset=True).items():
        setattr(current_user, key, value)
    db.add(current_user)
    await db.commit()
    return current_user