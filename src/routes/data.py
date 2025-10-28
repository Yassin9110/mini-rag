from fastapi import APIRouter, HTTPException, FastAPI, Depends, File, UploadFile, status
from fastapi.responses import JSONResponse
import os
from helpers.config import get_settings, Settings
from controllers import DataController, ProjectController
import aiofiles
from models import ResponseStatus

data_router = APIRouter(
    prefix="/api/v1/data",
    tags=["data"]
)


@data_router.post("/upload/{project_id}")
async def upload_data(project_id: str, file: UploadFile, app_settings: Settings = get_settings()):

    datacontroller = DataController()
    data_controller_valid, message = datacontroller.is_file_allowed(file)
    if not data_controller_valid:
        return JSONResponse(status_code=status.HTTP_400_BAD_REQUEST, content={ "message": message })
    
    project_dir_path = ProjectController().create_project_dir(project_id = project_id)
    file_path = datacontroller.generate_unique_filename(orig_file_name= file.filename, project_id= project_id)
    print( f"Saving file to path: {file_path}" )

    try:

        async with aiofiles.open(file_path, "wb") as f:

            while chunck := await file.read(app_settings.DEFAULT_FILE_CHUNCK_SIZE):
                await f.write(chunck)
    except Exception as e:
        print( f"Error saving file: {e}" )
        return JSONResponse(status_code= status.HTTP_400_BAD_REQUEST, content= {"message": ResponseStatus.FILE_UPLOAD_FAILED})
    return JSONResponse(status_code= status.HTTP_200_OK, content= {"status": ResponseStatus.SUCCESS})


