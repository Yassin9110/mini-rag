from enum import Enum

class ResponseStatus(str, Enum):
    SUCCESS = "success"
    ERROR = "error"
    PENDING = "pending"
    FILE_TYPE_NOT_ALLOWED = "file_type_not_allowed"
    FILE_SIZE_EXCEEDED = "file_size_exceeded"
    FILE_UPLOADED_SUCCESS = "file_uploaded_success :)"
    FILE_UPLOADED_FAILED = "file_upload_failed"
    FILE_PROCESSING_FAILED = "file_processing_failed"
    NO_FILES_TO_PROCESS = "no_files_to_process"
    