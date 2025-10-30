from pydantic import BaseModel
from typing import Optional

class ProcessDataRequest(BaseModel):
    file_id: str
    chunk_size: Optional[int] =1024 * 1024  # 1 MB by default
    overlap_size: Optional[int] = 0
    do_reset : Optional[bool] = False
    

