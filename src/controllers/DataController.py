from .BaseController import BaseController
from fastapi import UploadFile
from models import ResponseStatus
import re
from .ProjectController import ProjectController
import os

class DataController(BaseController):
    def __init__(self):
        super().__init__()

    def is_file_allowed(self, file: UploadFile) -> bool:
        if file.content_type not in self.app_settings.FILE_ALLOWED_EXTENSIONS:
            return False, ResponseStatus.FILE_TYPE_NOT_ALLOWED
        if file.size > self.app_settings.MAX_FILE_SIZE_MB * 1024 * 1024:
            return False, ResponseStatus.FILE_SIZE_EXCEEDED
        
        return True, ResponseStatus.FILE_UPLOADED_SUCCESS
    
    def generate_unique_filename(self, orig_file_name: str, project_id: str):
        print( "Generating unique filename..." )
        
        random_filename = self.generate_random_string()
        project_path = ProjectController().create_project_dir(project_id= project_id)

        cleaned_file_name = self.get_clean_filename(orig_file_name)

        new_path_file_name = os.path.join(project_path, random_filename + '_' + cleaned_file_name)

        while os.path.exists(new_path_file_name):
            random_filename = self.generate_random_string()
            new_path_file_name = os.path.join(project_path, random_filename + '_' + cleaned_file_name)

        print( f"Generated unique filename: {new_path_file_name}" )
        return new_path_file_name


    def get_clean_filename(self, orig_file_name: str):
        print( "Cleaning filename..." )
        cleaned_file_name = re.sub(r'[^\w.]', '', orig_file_name.strip())
        cleaned_file_name = cleaned_file_name.replace(" ", "_")
        return cleaned_file_name


