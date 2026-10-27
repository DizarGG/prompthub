from datetime import datetime
from pydantic import BaseModel, ConfigDict, EmailStr, Field


class UserCreate(BaseModel):
    username: str = Field(min_length=3, max_length=100)
    email: EmailStr
    password: str = Field(min_length=8, max_length=128)


class UserResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    username: str
    email: EmailStr
    is_active: bool


class AiGenerateRequest(BaseModel):
    # Сохраняем исходное имя promt для совместимости с ученическим API.
    promt: str = Field(min_length=3, max_length=2000)


class ProjectCreate(BaseModel):
    title: str = Field(min_length=1, max_length=200)
    description: str = Field(default='', max_length=2000)
    content: str = Field(min_length=1, max_length=20000)


class ProjectResponse(ProjectCreate):
    model_config = ConfigDict(from_attributes=True)
    id: int
    author_id: int
    likes: int
    created_at: datetime
