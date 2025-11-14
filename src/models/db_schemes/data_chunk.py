from pydantic import BaseModel, Field, field_validator
from typing import Optional
from bson.objectid import ObjectId

class DataChunk(BaseModel):
    _id: Optional[ObjectId] = None
    chunk_text: str = Field(..., min_length=1)
    metadata: Optional[dict] = None
    chunk_order: int = Field(..., gt=0)
    chunk_project_id: ObjectId 
    

    class Config:
        arbitrary_types_allowed = True
        json_encoders = {
            ObjectId: str
        }