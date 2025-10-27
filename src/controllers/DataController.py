from .BaseController import BaseController
from fastapi import UploadFile
from models import ResponseStatus

class DataController(BaseController):
    def __init__(self):
        super().__init__()

    def is_file_allowed(self, file: UploadFile) -> bool:
        if file.content_type not in self.app_settings.FILE_ALLOWED_EXTENSIONS:
            return False, ResponseStatus.FILE_TYPE_NOT_ALLOWED
        if file.size > self.app_settings.MAX_FILE_SIZE_MB * 1024 * 1024:
            return False, ResponseStatus.FILE_SIZE_EXCEEDED
        
        return True, ResponseStatus.FILE_UPLOADED_SUCCESS
    

    