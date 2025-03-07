from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from app.db.session import get_db
from app.models.address import Address
from app.schemas.address import AddressCreate, AddressCreateResponse, AddressResponse, AddressListResponse
from app.models.user import User
from app.api.deps import get_current_user

router = APIRouter(
    prefix="/addresses",
    tags=["addresses"],
)

# Create address endpoint
@router.post("/create", response_model=AddressCreateResponse)
async def create_address(
    address_in: AddressCreate, 
    db: AsyncSession = Depends(get_db), 
    current_user: User = Depends(get_current_user)
):
    if not current_user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="You are not authenticated!")

    new_address = Address(
        **address_in.model_dump(exclude_unset=True),    
        user_id=current_user.id
    )

    db.add(new_address)
    await db.commit()
    await db.refresh(new_address)

    return AddressCreateResponse(
        status="success",
        message="Address created successfully",
        data=AddressResponse.model_validate(new_address, from_attributes=True)
    )


# Update address endpoint
@router.put("/update/{address_id}", response_model=AddressCreateResponse)
async def update_address(
    address_id: int, 
    address_in: AddressCreate, 
    db: AsyncSession = Depends(get_db), 
    current_user: User = Depends(get_current_user)
):
    if not current_user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="You are not authenticated!")

    query = select(Address).where(Address.id == address_id)
    result = await db.execute(query)
    address = result.scalars().first()

    if not address:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Address not found")
    
    if address.user_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="You are not authorized to update this address")

    for attr, value in address_in.model_dump(exclude_unset=True).items():
        setattr(address, attr, value)

    await db.commit()
    await db.refresh(address)

    return AddressCreateResponse(
        status="success",
        message="Address updated successfully",
        data=AddressResponse.model_validate(address, from_attributes=True)
    )


# Get all addresses endpoint
@router.get("/", response_model=AddressListResponse)
async def get_all_addresses(
    db: AsyncSession = Depends(get_db), 
    current_user: User = Depends(get_current_user)
):
    if not current_user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="You are not authenticated!")

    query = select(Address)
    if current_user.role.value != "admin":
        query = query.where(Address.user_id == current_user.id)

    result = await db.execute(query)
    addresses = result.scalars().all()

    address_responses = [AddressResponse.model_validate(address) for address in addresses]

    return AddressListResponse(
        status="success",
        message="Addresses retrieved successfully",
        count=len(address_responses),
        data=address_responses
    )


# Get addresses by user_id
@router.get("/details/{user_id}", response_model=AddressListResponse)
async def get_addresses_by_user(
    user_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    if not current_user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="You are not authenticated!")

    # Allow admins to view any user's addresses, but regular users can only view their own
    if current_user.id != user_id and current_user.role.value != "admin":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="You are not authorized to view these addresses")

    query = select(Address).where(Address.user_id == user_id)
    result = await db.execute(query)
    addresses = result.scalars().all()

    if not addresses:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No addresses found for this user")

    address_responses = [AddressResponse.model_validate(address) for address in addresses]

    return AddressListResponse(
        status="success",
        message="Addresses retrieved successfully",
        count=len(address_responses),
        data=address_responses
    )
