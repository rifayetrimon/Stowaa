from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.session import get_db
from app.models.address import Address
from app.schemas.user import AddressCreate, AddressCreateResponse, AddressResponse
from app.api import deps
from app.models.user import User


router = APIRouter(
    prefix="/addresses",
    tags=["addresses"],
)


# create address endpoint
@router.post("/create", response_model=AddressCreateResponse)
async def create_address(address_in: AddressCreate, db: AsyncSession = Depends(get_db), current_user: User = Depends(deps.get_current_user)):
    
    if not current_user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="You are not authenticated!")
    
    new_address = Address(
        **address_in.model_dump(exclude_unset=True),    
        user_id=current_user.id
    )
    
    db.add(new_address)
    await db.commit()
    await db.refresh(new_address)

    response = AddressCreateResponse(
        status="success",
        message="Address created successfully",
        data=AddressResponse.model_validate(new_address, from_attributes=True)
    )

    return response



# update address endpoint
@router.put("/update/{address_id}", response_model=AddressCreateResponse)
async def update_address(address_id: int, address_in: AddressCreate, db: AsyncSession = Depends(get_db), current_user: User = Depends(deps.get_current_user)):
    
    if not current_user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="You are not authenticated!")
    
    address = await db.get(Address, address_id)
    if not address:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Address not found")
    
    if address.user_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="You are not authorized to update this address")
    
    for attr, value in address_in:
        setattr(address, attr, value)
    
    await db.commit()
    await db.refresh(address)

    response = AddressCreateResponse(
        status="success",
        message="Address updated successfully",
        data=AddressResponse.model_validate(address, from_attributes=True)
    )

    return response