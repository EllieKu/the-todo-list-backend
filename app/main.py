from fastapi import FastAPI
from contextlib import asynccontextmanager

from api.main import api_router
from database import create_db_and_tables

@asynccontextmanager
async def lifespan(app: FastAPI):
    create_db_and_tables()
    yield

app = FastAPI(
    title="Todo List API",
    description="A simple Todo List API built with FastAPI and SQLModel",
    version="1.0.0",
    lifespan=lifespan
)

app.include_router(api_router)
