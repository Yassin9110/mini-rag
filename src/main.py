from fastapi import FastAPI
from routes import base, data
from motor.motor_asyncio import AsyncIOMotorClient
from contextlib import asynccontextmanager
from helpers.config import get_settings




@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    app_settings = get_settings()
    app.mongodb_conn = AsyncIOMotorClient(app_settings.MONGODB_URL)
    app.mongodb_client = app.mongodb_conn[app_settings.MONGODB_DATABASE]
    print("Connected to MongoDB!")

    # Everything between startup and shutdown runs here
    yield

    # Shutdown
    app.mongodb_conn.close()
    print("Disconnected from MongoDB!")

app = FastAPI(lifespan=lifespan)

app.include_router(base.base_router)
app.include_router(data.data_router)
