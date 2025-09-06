from fastapi import APIRouter, Depends, Header
from sqlmodel import Session, select
from ...database import get_session
from ...models import User, UserCreate

router = APIRouter(prefix="/user", tags=["user"])

@router.post("/")
def create_user(user_create: UserCreate, session: Session = Depends(get_session)):
    statement = (select(User).where(User.username == user_create.username))
    existing_user = session.exec(statement).first()

    if existing_user:
        return {"message": "User already exists"}
    
    user = User(username=user_create.username)
    session.add(user)
    session.commit()
    session.refresh(user)
    return user
