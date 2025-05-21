from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
import logging

from app.db.session import get_db
from app.schemas.allheader import (
    BrowserCategoryCreate,
    BrowserCategoryResponse,
    BrowserCategoryUpdate,
    NavitemCreate,
)
from app.models.user import User
from app.api.deps import get_current_user
from app.services.allheader import BrowserCategoryService, NavitemService


router = APIRouter(prefix="/browser-category", tags=["browser-category"])
logger = logging.getLogger(__name__)

# create BrowserCategoryCreate
@router.post("/create", response_model=BrowserCategoryCreate)
async def create_browser_category(
    create_category: BrowserCategoryCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    new_category = await BrowserCategoryService.create_browser_category(db, create_category, current_user)
    return new_category

# all browser categories
@router.get("/", response_model=list[BrowserCategoryResponse])
async def get_browser_categories(
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),  
):
    return await BrowserCategoryService.get_browser_categories(db, user)

# update browser category
@router.put("/update/{category_id}", response_model=BrowserCategoryResponse)
async def update_browser_category(
    category_id: int,
    update_category: BrowserCategoryUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    updated_category = await BrowserCategoryService.update_browser_category(db, category_id, update_category, current_user)
    return updated_category

# create nav item 
@router.post("/navitem/create", response_model=NavitemCreate)
async def create_navitem(
    create_navitem: NavitemCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    new_navitem = await NavitemService.create_navitem(db, create_navitem, current_user)
    return new_navitem

# all nav items
@router.get("/navitem/", response_model=list[NavitemCreate])
async def get_navitems(
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),  
):
    return await NavitemService.get_navitems(db, user)

# update nav item
@router.put("/navitem/update/{navitem_id}", response_model=NavitemCreate)
async def update_navitem(
    navitem_id: int,
    update_navitem: NavitemCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    updated_navitem = await NavitemService.update_navitem(db, navitem_id, update_navitem, current_user)
    return updated_navitem