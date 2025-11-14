from .BaseDataModel import BaseDataModel
from .db_schemes import Project
from .enums.DataBaseEnum import DataBaseEnum

class ProjectModel(BaseDataModel):
    def __init__(self, db_client: object):
        super().__init__(db_client = db_client)
        self.collection = self.db_client[DataBaseEnum.COLLECTION_PROJECT_NAME.value]


    async def create_project(self, project_data: Project):
        # Use by_alias=True to use _id in MongoDB
        result = await self.collection.insert_one(project_data.model_dump(by_alias=True, exclude_none=True))
        project_data.id = result.inserted_id  # Set the id field (which maps to _id)
        return project_data
    
    async def get_project_or_create_one(self, project_id: str):
        record = await self.collection.find_one({"project_id": project_id})

        if record is None:
            project = Project(project_id=project_id)
            project = await self.create_project(project)
            return project
        
        return Project(**record)
    

    async def get_all_projects(self, page: int = 1, page_size: int = 10):
        
        total_documents = await self.collection.count_documents({})

        total_pages = total_documents // page_size
        if total_documents % page_size > 0:
            total_pages += 1


        cursor = self.collection.find().skip((page - 1) * page_size).limit(page_size)

        projects = [Project(**doc) async for doc in cursor]

        return projects, total_pages
     
