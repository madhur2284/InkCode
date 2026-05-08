from fastapi import APIRouter, status, Depends, UploadFile, File, status, HTTPException
from schemas.auth import UserResponse, UserCreate, Token, UserLogin, ChangePassword, UserUpdate, RefreshToken
from typing import Optional
from models.db_models import User
from sqlalchemy.ext.asyncio import AsyncSession
from database import get_db
from services.cloudinary import cloudinary_upload, cloudinary_delete
from services.auth import hash_password, verify_password, generate_access_token, generate_refresh_token, get_current_user, decode_token
from crud.auth import get_user_by_email, get_user_by_username, add_user, get_user_by_id_token_version
from services.slug import create_unique_slug
from fastapi.security import OAuth2PasswordRequestForm
from jose import JWTError

router = APIRouter(prefix="/auth", tags=["auth"])

@router.post(path='/register', status_code=status.HTTP_201_CREATED, response_model=UserResponse)
async def register(form_data : UserCreate = Depends(UserCreate.form_data), avatar_image: Optional[UploadFile] = File(default=None), db: AsyncSession = Depends(get_db)):
    if await get_user_by_username(form_data.username, db):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="username already exist")
    if await get_user_by_email(form_data.email, db):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Email id alrady exist")

    avatar_url = None
    avatar_public_id = None
    if avatar_image:
        result = await cloudinary_upload(avatar_image)
        if result:
            avatar_url = result.get("avatar_url")
            avatar_public_id = result.get("avatar_public_id")
 
    hashed_password = await hash_password(form_data.password)
    slug = await create_unique_slug(form_data.username, db, User)

    try:
        user = await add_user(email=form_data.email, username=form_data.username, bio=form_data.bio, hashed_password=hashed_password, avatar_url=avatar_url, avatar_public_id = avatar_public_id, db=db, slug=slug)
        if not user:
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Failed to register user")
        return user
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Failed to register user: {e}")
    

@router.post(path='/login', status_code=status.HTTP_200_OK, response_model=Token)
async def login_user(detail: OAuth2PasswordRequestForm = Depends(), db: AsyncSession = Depends(get_db)):
    user = await get_user_by_username(detail.username, db)
    if not user:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="username didn't exist")
    
    if not await verify_password(detail.password, user.hashed_password):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Wrong Password")
    
    try:
        access_token = generate_access_token({"id": user.id, "role": user.role, "token_version": user.token_version})
        refresh_token = generate_refresh_token({"id": user.id, "role": user.role, "token_version": user.token_version})
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Error: {e}")
    
    return {"access_token": access_token, "refresh_token": refresh_token}


@router.post(path='/logout', status_code=status.HTTP_200_OK)
async def logout(user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    user.token_version = user.token_version+1
    await db.commit()
    return {"Message": "Logout successfully"}


@router.post(path='/change_password', status_code=status.HTTP_200_OK)
async def change_password(password: ChangePassword, db: AsyncSession = Depends(get_db), user: User = Depends(get_current_user)):
    if not await verify_password(password.old_password, user.hashed_password):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Wrong Password")

    try:
        hashed_password = await hash_password(password.new_password)
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Error: {e}")
    
    user.hashed_password = hashed_password
    user.token_version = user.token_version+1
    try:
        await db.commit()
        return {"message": "Password changed successfully"}
    except Exception as e:
        await db.rollback()
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Error: {e}")


@router.get(path='/me', status_code=status.HTTP_200_OK, response_model=UserResponse)
async def get_me(user: User = Depends(get_current_user)):
    return user

@router.patch(path="/me", status_code=status.HTTP_200_OK, response_model=UserResponse)
async def update_user(new_detail: UserUpdate = Depends(UserUpdate.update), avatar_image: Optional[UploadFile] = File(default=None),db: AsyncSession = Depends(get_db), user: User = Depends(get_current_user)):
    flag = False
    for key, value in new_detail.model_dump(exclude_none=True).items():
        flag = True
        setattr(user, key, value)

    if avatar_image:
        flag = True
        if user.avatar_post_id:
            await cloudinary_delete(user.avatar_post_id)
        result = await cloudinary_upload(avatar_image)
        user.avatar_url = result.get("avatar_url")
        user.avatar_post_id = result.get("avatar_public_id")


    if flag:
        try:
            await db.commit()
            await db.refresh(user)
            return user
        except Exception as e:
            await db.rollback()
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Error: {e}")


@router.post(path='/refresh', status_code=status.HTTP_201_CREATED, response_model=Token)
async def refresh(token: RefreshToken, db: AsyncSession = Depends(get_db)):
    try:
        payload = decode_token(token.token)
    except JWTError as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Error: {e}")

    if payload.get("type") != "refresh":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Token type is not refresh")    

    try:
        user: User = await get_user_by_id_token_version(payload.get("id"), payload.get("token_version"), db)
    except:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=f"user didn't exist")
    
    access_token = generate_access_token({"id": user.id, "role": user.role, "token_version": user.token_version})
    refresh_token = generate_refresh_token({"id": user.id, "role": user.role, "token_version": user.token_version})

    return {
        "access_token": access_token,
        "refresh_token": refresh_token
    }


@router.delete(path='/me', status_code=status.HTTP_200_OK)
async def delete_user(user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    user.is_active = False
    await db.commit()

    return {"message": "account deleted sucessfully"}
    


