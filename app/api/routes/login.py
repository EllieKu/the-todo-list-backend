from fastapi import APIRouter, Depends
from sqlmodel import Session, select
from ...database import get_session
from ...models import User

router = APIRouter(prefix="/login", tags=["login"])

@router.post("/")
def login_user(username: str, session: Session = Depends(get_session)):
    statement = select(User).where(User.username == username)
    existing_user = session.exec(statement).first()

    if not existing_user:
        return {"message": "User not found"}

    return {
        "user_id": existing_user.id,
        "message": "Login successfully"
    }