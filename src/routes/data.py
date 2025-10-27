from fastapi import APIRouter, HTTPException, FastAPI, Depends, File, UploadFile, status
from fastapi.responses import JSONResponse
import os
from helpers.config import get_settings, Settings
from controllers import DataController


data_router = APIRouter(
    prefix="/api/v1/data",
    tags=["data"]
)


@data_router.post("/upload")
async def upload_data(file: UploadFile):

    data_controller_valid, message = DataController().is_file_allowed(file)
    if data_controller_valid:
        return JSONResponse(status_code=status.HTTP_200_OK, content={ "message": message })
    else:
        return JSONResponse(status_code=status.HTTP_400_BAD_REQUEST, content={ "message": message })


