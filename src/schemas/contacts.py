from typing import Optional
from datetime import date, datetime

from pydantic import BaseModel, EmailStr, Field

from src.schemas.user import UserResponse

class ContactSchema(BaseModel):
    first_name: str = Field(min_length=1, max_length=50)
    last_name: str = Field(min_length=1, max_length=50)
    email: EmailStr = Field(max_length=50)
    phone: str = Field(min_length=1, max_length=50)
    birthday: date
    additional_data: Optional[str] = Field(max_length=250)




class ContactUpdateSchema(ContactSchema):
    first_name: Optional[str] = Field(min_length=1, max_length=50)
    last_name: Optional[str] = Field(min_length=1, max_length=50)
    email: Optional[EmailStr] = Field(max_length=50)
    phone: Optional[str] = Field(min_length=1, max_length=50)
    birthday: Optional[date]
    additional_data: Optional[str] = Field(max_length=250)



class ContactResponse(BaseModel):
    id: int
    first_name: str
    last_name: str
    email: str
    phone: str
    birthday: date
    additional_data: Optional[str]
    created_at: datetime
    updated_at: datetime
    user: UserResponse | None

    class Config:
        from_attributes = True
