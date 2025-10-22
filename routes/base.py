from fastapi import FastAPI, APIRouter

base_router = APIRouter()

@base_router.get("/")
def welcome():
    return {"message": "Welcome to the Mini RAG FastAPI application!!"}