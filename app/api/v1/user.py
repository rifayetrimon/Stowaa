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

router = APIRouter(
    prefix="/users",
    tags=["users"], 
)


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


# # Get current user
# @router.get("/profile", response_model=UserRead)
# async def get_user_profile(current_user: User = Depends(get_current_user)):
#     current_user_data = UserRead.model_validate(current_user)
#     return current_user_data


@router.get("/profile", response_model=UserRead)
async def get_user_profile(current_user: User = Depends(get_current_user)):
    # Manually map SQLAlchemy instance to the Pydantic schema
    current_user_data = UserRead(
        id=current_user.id,
        name=current_user.name,
        email=current_user.email,
        is_active=current_user.is_active,
    )
    return current_user_data




# Update user profile
@router.put("/profile-update", response_model=UserRead)
async def update_user_profile(
    user_in: UserUpdate, 
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    for key, value in user_in.model_dump(exclude_unset=True).items():
        setattr(current_user, key, value)
    db.add(current_user)
    await db.commit()
    return current_user