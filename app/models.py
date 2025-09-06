import uuid
import re
from datetime import date

from sqlmodel import SQLModel, Field
from typing import Optional, Any, List
from pydantic import field_validator, field_serializer

class TodoBase(SQLModel):
    task: str = Field(max_length=255)
    deadline: date
    priority: int = Field(ge=0, le=2, default=0)
    is_done: int = Field(default=0, ge=0, le=1)
    user_id: str
    
    @field_validator('deadline', mode='before')
    @classmethod
    def validate_deadline_format(cls, v):
        if isinstance(v, str):
            return yyyymmdd_to_date(v)
        elif isinstance(v, date):
            return v
        else:
            raise ValueError('deadline must be a date or yyyymmdd string')
    
    @field_serializer('deadline')
    def serialize_deadline(self, value: date) -> str:
        return date_to_yyyymmdd(value)

class Todo(TodoBase, table=True):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()), primary_key=True)

class TodoCreate(SQLModel):
    task: str = Field(max_length=255)
    deadline: date
    priority: int = Field(default=0, ge=0, le=2)
    is_done: int = Field(default=0, ge=0, le=1)

    @field_validator('deadline', mode='before')
    @classmethod
    def validate_deadline_format(cls, v):
        if isinstance(v, str):
            return yyyymmdd_to_date(v)
        else:
            raise ValueError('deadline must be a yyyymmdd string')
    
    @field_serializer('deadline')
    def serialize_deadline(self, value: date) -> str:
        return date_to_yyyymmdd(value)

class TodoUpdate(SQLModel):
    task: Optional[str] = Field(default=None, max_length=255)
    deadline: Optional[date] = None
    priority: Optional[int] = Field(default=None, ge=0, le=2)
    is_done: Optional[int] = Field(default=None, ge=0, le=1)
    
    @field_validator('deadline', mode='before')
    @classmethod
    def validate_deadline_format(cls, v):
        if v is None:
            return None
        if isinstance(v, str):
            return yyyymmdd_to_date(v)
        elif isinstance(v, date):
            return v
        else:
            raise ValueError('deadline must be a date or yyyymmdd string')
    
    @field_serializer('deadline')
    def serialize_deadline(self, value: Optional[date]) -> Optional[str]:
        return date_to_yyyymmdd(value) if value is not None else None

class TodoPublic(SQLModel):
    id: str
    task: str
    deadline: date
    priority: int
    is_done: int
    
    @field_serializer('deadline')
    def serialize_deadline(self, value: date) -> str:
        return date_to_yyyymmdd(value)

class TodosResponse(SQLModel):
    todos: List[TodoPublic]
    todos_total: int
    todos_pages: int

def yyyymmdd_to_date(value: str) -> date:
    if not re.match(r'^\d{8}$', value):
        raise ValueError('deadline must be in yyyymmdd format')
    
    try:
        year = int(value[:4])
        month = int(value[4:6])
        day = int(value[6:8])
        
        if year < 1911:
            raise ValueError('Invalid year in deadline')
        if month < 1 or month > 12:
            raise ValueError('Invalid month in deadline')
        if day < 1 or day > 31:
            raise ValueError('Invalid day in deadline')
        
        return date(year, month, day)
            
    except ValueError as e:
        if 'invalid literal' in str(e):
            raise ValueError('deadline must contain only digits')
        raise e

def date_to_yyyymmdd(value: date) -> str:
    return value.strftime('%Y%m%d')

class UserBase(SQLModel):
    username: str = Field(unique=True, max_length=50)
    preference: Optional[str] = None

class User(UserBase, table=True):
    id: Optional[str] = Field(default_factory=lambda: str(uuid.uuid4()), primary_key=True)

class UserCreate(SQLModel):
    username: str = Field(max_length=50)
