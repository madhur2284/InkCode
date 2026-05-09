from pydantic import BaseModel, Field, EmailStr
from typing import Optional, Literal, List
from datetime import datetime
from fastapi import Form

class UserCreate(BaseModel):
    username: str = Field(description="Unique Username")
    email: str = Field(description="Unique email ID")
    password: str = Field(description="Password given by user", max_length=72)
    bio: Optional[str] = Field(description="Bio of the user", default=None)

    @classmethod
    def form_data(
        cls,
        username: str = Form(),
        email: EmailStr = Form(),
        password: str = Form(),
        bio: Optional[str] = Form(default=None)
    ):
        return cls(username=username, email=email, password=password, bio=bio)
    
class UserResponse(BaseModel):
    id: int
    username: str
    email: EmailStr
    bio: Optional[str]
    avatar_url: str
    created_at: datetime
    model_config={"from_attributes": True}


class UserLogin(BaseModel):
    username: str = Field(description="Username")
    password: str = Field(description="password")


class Token(BaseModel):
    access_token: str
    refresh_token: str
    model_config = {"from_attributes": True}

class ChangePassword(BaseModel):
    new_password: str
    old_password: str

class UserUpdate(BaseModel):
    bio: Optional[str] = Field(description="bio")

    @classmethod
    def update(
        cls,
        bio: Optional[str] = Form()
    ):
        return cls(bio=bio)
    

class RefreshToken(BaseModel):
    token: str