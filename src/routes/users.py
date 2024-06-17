import pickle

import cloudinary

from fastapi_limiter.depends import RateLimiter
from fastapi import APIRouter, Depends, UploadFile, File
from sqlalchemy.ext.asyncio import AsyncSession

from src.conf.config import config
from src.entity.models import User
from src.database.db import get_db
from src.repository import users as repository_users
from src.schemas.user import UserResponse
from src.services.auth import auth_service


router = APIRouter(prefix='/users', tags=['users'])
configurating = cloudinary.config(
    cloud_name=config.CLD_NAME,
    api_key=config.CLD_API_KEY,
    api_secret=config.CLD_API_SECRET,
    secure=True
    )
import cloudinary.uploader

@router.get('/me', response_model=UserResponse,
            dependencies=[Depends(RateLimiter(times=1, seconds=20))])
async def get_current_user(user: User = Depends(auth_service.get_current_user)):
    return user

@router.patch('/avatar', 
              response_model=UserResponse,
              dependencies=[Depends(RateLimiter(times=1, seconds=20))])
async def update_avatar(file: UploadFile = File(), 
                           user: User = Depends(auth_service.get_current_user), 
                           db: AsyncSession = Depends(get_db)):
    
    public_id = f"lection_26/{user.email}"
    res = cloudinary.uploader.upload(file.file, public_id=public_id, owerite=True)
    res_url = cloudinary.CloudinaryImage(public_id).build_url(
        width=250, height=250, crop='fill', version=res.get("version"))
    
    user = await repository_users.update_avatar_url(user.email, res_url, db)
    auth_service.cache.set(user.email, pickle.dumps(user))
    auth_service.cache.expire(user.email, 300)
    return user