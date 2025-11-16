from .BaseDataModel import BaseDataModel
from .db_schemes import Asset
from models.enums.DataBaseEnum import DataBaseEnum
from bson import ObjectId

class AssetModel(BaseDataModel):
    def __init__(self, db_client):
        super().__init__(db_client)
        self.collection = self.db_client[DataBaseEnum.COLLECTION_ASSET_NAME.value]

    @classmethod
    async def create_instance(cls, db_client):
        instance = cls(db_client)
        await instance.init_collection()
        return instance
    
    async def init_collection(self):
        all_collections = await self.db_client.list_collection_names()
        if DataBaseEnum.COLLECTION_ASSET_NAME.value not in all_collections:
            await self.db_client.create_collection(DataBaseEnum.COLLECTION_ASSET_NAME.value)
            indexes = Asset.get_indexes()
            for index in indexes:
                await self.collection.create_index(index["key"], name=index["name"], unique=index["unique"])


    async def create_asset(self, asset_data: Asset):
        # Remove the id field completely when inserting
        data_to_insert = asset_data.model_dump(by_alias=True, exclude_none=True)
        if "_id" in data_to_insert and data_to_insert["_id"] is None:
            del data_to_insert["_id"]  # Remove None _id values
        
        result = await self.collection.insert_one(data_to_insert)
        asset_data.id = result.inserted_id  # Now set the ID that MongoDB generated
        return asset_data
    
    async def get_all_project_assets(self, asset_project_id:str, asset_type: str = None):
        
        records = await self.collection.find(
            {"asset_project_id": ObjectId(asset_project_id) if isinstance(asset_project_id, str) else asset_project_id,
             "asset_type": asset_type
             
             }).to_list(length=None)
        
        return [Asset(**record) for record in records]
    
    async def get_asset_record(self, asset_project_id: str, asset_name: str):
        record = await self.collection.find_one(
            {"asset_project_id": ObjectId(asset_project_id) if isinstance(asset_project_id, str) else asset_project_id,
                "asset_name": asset_name
             })
        if record:
            return Asset(**record)
        return None
    


    
