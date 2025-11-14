from .BaseDataModel import BaseDataModel
from .db_schemes import Project, DataChunk
from .enums.DataBaseEnum import DataBaseEnum
from bson.objectid import ObjectId

class ChunkModel(BaseDataModel):

    def __init__(self, db_client: object):
        super().__init__(db_client = db_client)
        self.collection = self.db_client[DataBaseEnum.COLLECTION_CHUNK_NAME.value]

    async def create_data_chunk(self, chunk: DataChunk):
        result = await self.collection.insert_one(chunk.model_dump(by_alias=True, exclude_none=True))
        chunk.id = result.inserted_id  # Set the id field (which maps to _id)
        return chunk
    
    async def get_chunk(self, chunk_id: str):
        result = await self.collection.find_one({"_id": ObjectId(chunk_id)})

        if result is None:
            return None
        
        return DataChunk(**result)
    
    async def insert_batch_chunks(self, chunks: list, batch_size: int= 100):
        for i in range(0, len(chunks), batch_size):
            batch = chunks[i:i + batch_size]
            # Convert each DataChunk to dict using model_dump
            batch_dicts = [chunk.model_dump(by_alias=True, exclude_none=True) for chunk in batch]
            await self.collection.insert_many(batch_dicts)

        return len(chunks)
    
    async def delete_chunks_by_project_id(self, project_id: ObjectId):
        result = await self.collection.delete_many({"chunk_project_id": project_id})
        return result.deleted_count

