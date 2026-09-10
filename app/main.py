from contextlib import asynccontextmanager
from app.api.repositories import router as repositories_router
from fastapi import FastAPI
from app.api.users import router as users_router
from app.db.database import create_tables
from app.api.chat import router as chat_router
from app.api.auth import router as auth_router
from fastapi.middleware.cors import CORSMiddleware
@asynccontextmanager
async def lifespan(app: FastAPI):
    await create_tables()
    yield


app = FastAPI(
    title="DebugPilot API",
    lifespan=lifespan,
)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.include_router(auth_router)
app.include_router(users_router)
app.include_router(repositories_router)
app.include_router(chat_router)
