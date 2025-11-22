from pydantic import BaseModel, Field, field_validator
from typing import Optional
from bson.objectid import ObjectId

class DataChunk(BaseModel):
    _id: Optional[ObjectId] = None
    chunk_text: str = Field(..., min_length=1)
    metadata: Optional[dict] = None
    chunk_order: int = Field(..., gt=0)
    chunk_project_id: ObjectId 
    chunk_asset_id: ObjectId
    

    class Config:
        arbitrary_types_allowed = True
        json_encoders = {
            ObjectId: str
        }

    @classmethod
    def get_indexes(cls):

        return [
            {
                "key": [("chunk_project_id", 1)],
                "name": "chunk_project_id_index_1",
                "unique": False
            }
        ]
    
class RetrievedDocument(BaseModel):
    text: str
    score: float
