from fastapi import FastAPI
from routes import base, data
from motor.motor_asyncio import AsyncIOMotorClient
from contextlib import asynccontextmanager
from helpers.config import get_settings
from stores.llm.LLMProviderFactory import LLMProviderFactory



@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    app_settings = get_settings()
    llm_factory = LLMProviderFactory(app_settings)
    app.mongodb_conn = AsyncIOMotorClient(app_settings.MONGODB_URL)
    app.mongodb_client = app.mongodb_conn[app_settings.MONGODB_DATABASE]
    print("Connected to MongoDB!")
    app.generation_client = llm_factory.create_provider(app_settings.GENERATION_BACKEND)
    app.generation_client.set_generation_model(model_id= app_settings.GENERATION_MODEL)
    app.embedding_client = llm_factory.create_provider(app_settings.EMBEDDING_BACKEND)
    app.embedding_client.set_embedding_model(model_id= app_settings.EMBEDDING_MODEL)

    # Everything between startup and shutdown runs here
    yield

    # Shutdown
    app.mongodb_conn.close()
    print("Disconnected from MongoDB!")

app = FastAPI(lifespan=lifespan)

app.include_router(base.base_router)
app.include_router(data.data_router)
