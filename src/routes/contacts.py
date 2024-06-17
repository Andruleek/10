from typing import List

from fastapi import APIRouter, HTTPException, Depends, Path, Query
from sqlalchemy.ext.asyncio import AsyncSession

from src.database.db import get_db
from src.entity.models import User, Role
from src.repository import contacts as repositories_contacts
from src.schemas.contact import ContactSchema, ContactUpdateSchema, ContactResponse
from src.services.auth import auth_service
from src.services.roles import RoleAccess

router = APIRouter(
    prefix="/contacts",
    tags=["contacts"])

access_to_route_all = RoleAccess([Role.admin, Role.moderator])

@router.get("/", response_model=List[ContactResponse])
async def get_contacts(limit: int = Query(10, ge=10, le=500),
                        offset: int = Query(0, ge=0),
                        db: AsyncSession = Depends(get_db),
                        user: User = Depends(auth_service.get_current_user)):
    contacts = await repositories_contacts.get_contacts(limit, offset, db, user)
    return contacts

@router.get('/all', response_model=list[ContactResponse], dependencies=[Depends(access_to_route_all)])
async def get_all_contacts(limit: int = Query(10, ge=10, le=500),
                    offset: int = Query(0, ge=0),
                    db: AsyncSession = Depends(get_db),
                    user: User = Depends(auth_service.get_current_user)):
    contacts = await repositories_contacts.get_all_contacts(limit, offset, db)
    return contacts

@router.get("/{contact_id}", response_model=ContactResponse)
async def get_contact(contact_id: int = Path(ge=1),
                   db: AsyncSession = Depends(get_db),
                   user: User = Depends(auth_service.get_current_user)):
    contact = await repositories_contacts.get_contact(contact_id, db, user)
    if contact is None:
        raise HTTPException(
            status_code=404,
            detail=f"User not found")
    return contact

@router.get("/contacts/{search}", response_model=List[ContactResponse])
async def search_contacts(contact_data: str,
                         db: AsyncSession = Depends(get_db),
                         user: User = Depends(auth_service.get_current_user)):
    contacts = await repositories_contacts.search_contacts(contact_data, db, user)
    if contacts is None:
        raise HTTPException(
            status_code=404,
            detail=f"Users not found")
    return contacts

@router.get("/contacts/", response_model=List[ContactResponse])
async def get_contacts_with_birthday_in_period(count_of_days: int = Query(1, ge=1, le=7), 
                                            limit: int = Query(10, ge=10, le=500),
                                            offset: int = Query(0, ge=0),
                                            db: AsyncSession = Depends(get_db),
                                            user: User = Depends(auth_service.get_current_user)):
    contacts = await repositories_contacts.get_contacts_with_birthday_in_period(count_of_days, limit, offset, db, user)
    if contacts is None:
        raise HTTPException(
            status_code=404,
            detail=f"Users not found")
    return contacts
    
    

@router.post("/", response_model=ContactResponse, status_code=201)
async def create_contact(body: ContactSchema,
                      db: AsyncSession = Depends(get_db),
                      user: User = Depends(auth_service.get_current_user)):
    contact = await repositories_contacts.create_contact(body, db, user)
    return contact

@router.put("/{contact_id}")
async def update_contact(body: ContactUpdateSchema,
                      contact_id: int = Path(ge=1),
                      db: AsyncSession = Depends(get_db),
                      user: User = Depends(auth_service.get_current_user)):
    contact = await repositories_contacts.update_contact(contact_id, body, db, user)
    if contact is None:
        raise HTTPException(
            status_code=404,
            detail=f"User not found")
    return contact

@router.delete("/{contact_id}", status_code=204)
async def delete_contact(contact_id: int = Path(ge=1),
                      db: AsyncSession = Depends(get_db),
                      user: User = Depends(auth_service.get_current_user)):
    contact = await repositories_contacts.delete_contact(contact_id, db, user)
    if contact is None:
        raise HTTPException(
            status_code=404,
            detail="User not found")
    return contact
