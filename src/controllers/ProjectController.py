from .BaseController import BaseController
from fastapi import UploadFile
from models.enums import ResponseStatus
import os

class ProjectController(BaseController):
    def __init__(self):
        super().__init__()

    def create_project_dir(self, project_id) -> str:
        print("In create project dir function \n")
        project_dir =  os.path.join(self.file_dir, project_id)

        os.makedirs(project_dir, exist_ok= True)
        print(f"directory created in: {project_dir}")
        return project_dir