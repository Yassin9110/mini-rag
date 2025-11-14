from pydantic import BaseModel, Field, field_validator
from typing import Optional
from bson.objectid import ObjectId

class Project(BaseModel):
    id: Optional[ObjectId] = Field(None, alias="_id")  # Use alias for MongoDB _id
    project_id: str = Field(..., min_length=1)

    @field_validator("project_id")
    def validate_project_id(cls, v):
        if not v.isalnum():
            raise ValueError("project_id must be alphanumeric")
        return v
    
    class Config:
        arbitrary_types_allowed = True
        populate_by_name = True  # Allow both id and _id
        json_encoders = {
            ObjectId: str  # Convert ObjectId to string for JSON
        }