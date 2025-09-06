from fastapi import APIRouter

from .routes import todo, user, login

api_router = APIRouter()
api_router.include_router(todo.router)
api_router.include_router(user.router)
api_router.include_router(login.router)