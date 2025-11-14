from fastapi import APIRouter, HTTPException, FastAPI, Depends, File, UploadFile, status, Request
from fastapi.responses import JSONResponse
import os
from helpers.config import get_settings, Settings
from controllers import DataController, ProjectController, ProcessController
import aiofiles
from models import ResponseStatus
from routes import ProcessDataRequest
from models.ProjectModel import ProjectModel
from models.ChunkModel import ChunkModel
from models.db_schemes import DataChunk


data_router = APIRouter(
    prefix="/api/v1/data",
    tags=["data"]
)


@data_router.post("/upload/{project_id}")
async def upload_data(request: Request, project_id: str, file: UploadFile, app_settings: Settings = get_settings()):

    project_model = ProjectModel(db_client= request.app.mongodb_client)
    project = await project_model.get_project_or_create_one(project_id= project_id)
    # print all project attributes

    print("Project details: ", project)
    print("Project ID: ", project.id)  # Now use .id instead of ._id

    datacontroller = DataController()
    data_controller_valid, message = datacontroller.is_file_allowed(file)
    if not data_controller_valid:
        return JSONResponse(status_code=status.HTTP_400_BAD_REQUEST, content={ "message": message })
    
    project_dir_path = ProjectController().create_project_dir(project_id = project_id)
    file_path, file_id = datacontroller.generate_unique_filpath(orig_file_name= file.filename, project_id= project_id)
    print( f"Saving file to path: {file_path}" )

    try:

        async with aiofiles.open(file_path, "wb") as f:

            while chunck := await file.read(app_settings.DEFAULT_FILE_CHUNK_SIZE):
                await f.write(chunck)
    except Exception as e:
        print( f"Error saving file: {e}" )
        return JSONResponse(status_code= status.HTTP_400_BAD_REQUEST, content= {"message": ResponseStatus.FILE_UPLOAD_FAILED})
    return JSONResponse(
        content= {
            "status": ResponseStatus.SUCCESS,
            "file_id": file_id,
            "project_id": str(project.id)
             })




@data_router.post("/process/{project_id}")
async def process_data(request : Request, project_id: str, process_request: ProcessDataRequest):
    
    file_id = process_request.file_id
    chunk_size = process_request.chunk_size
    overlap_size = process_request.overlap_size
    do_reset = process_request.do_reset

    project_model = ProjectModel(db_client= request.app.mongodb_client)
    project = await project_model.get_project_or_create_one(project_id= project_id)



    process_controller = ProcessController(project_id= project_id)

    file_content = process_controller.get_file_content(file_id= file_id)

    file_chunks = process_controller.process_file(file_content= file_content, chunk_size= chunk_size, chunk_overlap= overlap_size)

    if not file_chunks:
        return JSONResponse(status_code= status.HTTP_400_BAD_REQUEST, content= {"message": ResponseStatus.FILE_PROCESSING_FAILED})
    print("Chunck sample: ", file_chunks[0])
    
    file_chunks_records = [
        DataChunk(
            chunk_text= chunk.page_content,
            metadata= chunk.metadata,
            chunk_order = i+1,
            chunk_project_id = project.id

        )
        for i, chunk in enumerate(file_chunks)
    ]
    
    chunk_model = ChunkModel(db_client= request.app.mongodb_client)

    if do_reset:
        _ = await chunk_model.delete_chunks_by_project_id(project_id= project.id)
        

    num_records = await chunk_model.insert_batch_chunks(chunks= file_chunks_records, batch_size= 100)

    return JSONResponse(
        content= {
            "status": ResponseStatus.SUCCESS,
            "num_chunks": num_records
             })
    

    
