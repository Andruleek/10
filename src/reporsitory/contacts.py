from datetime import datetime, timedelta

from sqlalchemy import or_
from sqlalchemy import select
from sqlalchemy.sql import func
from sqlalchemy.ext.asyncio import AsyncSession

from src.entity.models import Contact, User
from src.schemas.contact import ContactSchema, ContactUpdateSchema



async def get_contacts(limit: int, offset: int,
                       db:AsyncSession, user: User):
    query = select(Contact).filter_by(user=user).limit(limit).offset(offset)
    contacts = await db.execute(query)
    return contacts.scalars().all()

async def get_all_contacts(limit: int, offset: int, db: AsyncSession):
    stmt = select(Contact).offset(offset).limit(limit)
    contacts = await db.execute(stmt)
    return contacts.scalars().all()

async def get_contact(contact_id: int, db:AsyncSession, user: User):
    query = select(Contact).filter_by(id=contact_id, user=user)
    contact = await db.execute(query)
    return contact.scalar_one_or_none()


async def create_contact(body: ContactSchema, db:AsyncSession, user: User):
    contact = Contact(**body.model_dump(), user=user)
    db.add(contact)
    await db.commit()
    await db.refresh(contact)
    return contact

async def update_contact(contact_id: int,
                      body: ContactUpdateSchema, 
                      db:AsyncSession, user: User):
    query = select(Contact).filter_by(id=contact_id, user=user)
    result = await db.execute(query)
    contact = result.scalar_one_or_none()
    if contact:
        contact.first_name = body.first_name
        contact.last_name = body.last_name
        contact.email = body.email
        contact.phone = body.phone
        contact.birthday = body.birthday
        contact.additional_data = body.additional_data
        await db.commit()
        await db.refresh(contact)
        return contact


async def delete_contact(contact_id: int, db:AsyncSession, user: User):
    query = select(Contact).filter_by(id=contact_id, user=user)
    result = await db.execute(query)
    contact = result.scalar_one_or_none()
    if contact:
        await db.delete(contact)
        await db.commit()
    return contact



async def search_contacts(query: str, db: AsyncSession, user: User):
    stmt = select(Contact).where(
        or_(
            Contact.first_name.ilike(f'%{query}%'),
            Contact.last_name.ilike(f'%{query}%'),
            Contact.email.ilike(f'%{query}%')
        )
    ).filter_by(user=user)
    result = await db.execute(stmt)
    result = result.scalars().all()
    return result


async def get_contacts_with_birthday_in_period(count_of_days: int, limit: int, offset: int,
                                               db: AsyncSession, user: User):
    today = datetime.today().date()
    end_date = today + timedelta(days=count_of_days)
    today_str = today.strftime("%m-%d")
    end_date_str = end_date.strftime("%m-%d")

    if today.month <= end_date.month:
        query = select(Contact).where(
            func.to_char(Contact.birthday, "MM-DD").between(today_str, end_date_str)
        ).filter_by(user=user).limit(limit).offset(offset)
    else:
        query = select(Contact).where(
            or_(
                func.to_char(Contact.birthday, "MM-DD") >= today_str,
                func.to_char(Contact.birthday, "MM-DD") <= end_date_str
            )
        ).filter_by(user=user).limit(limit).offset(offset)
        
    result = await db.execute(query)
    contacts = result.scalars().all()
    return contacts