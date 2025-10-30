from fastapi import APIRouter, HTTPException, FastAPI, Depends, File, UploadFile, status
from fastapi.responses import JSONResponse
import os
from helpers.config import get_settings, Settings
from controllers import DataController, ProjectController, ProcessController
import aiofiles
from models import ResponseStatus
from routes import ProcessDataRequest


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
    file_path, file_id = datacontroller.generate_unique_filpath(orig_file_name= file.filename, project_id= project_id)
    print( f"Saving file to path: {file_path}" )

    try:

        async with aiofiles.open(file_path, "wb") as f:

            while chunck := await file.read(app_settings.DEFAULT_FILE_CHUNCK_SIZE):
                await f.write(chunck)
    except Exception as e:
        print( f"Error saving file: {e}" )
        return JSONResponse(status_code= status.HTTP_400_BAD_REQUEST, content= {"message": ResponseStatus.FILE_UPLOAD_FAILED})
    return JSONResponse(status_code= status.HTTP_200_OK, content= {"status": ResponseStatus.SUCCESS, "file_id": file_id})




@data_router.post("/process/{project_id}")
async def process_data(project_id: str, request: ProcessDataRequest):
    
    file_id = request.file_id
    chunk_size = request.chunk_size
    overlap_size = request.overlap_size


    process_controller = ProcessController(project_id= project_id)

    file_content = process_controller.get_file_content(file_id= file_id)

    file_chunks = process_controller.process_file(file_content= file_content, chunk_size= chunk_size, chunk_overlap= overlap_size)

    if not file_chunks:
        return JSONResponse(status_code= status.HTTP_400_BAD_REQUEST, content= {"message": ResponseStatus.FILE_PROCESSING_FAILED})
    print("Chunck sample: ", file_chunks[0])
    return JSONResponse(status_code= status.HTTP_200_OK, content= {"status": ResponseStatus.SUCCESS, "chunks length": len(file_chunks)})

    

    
