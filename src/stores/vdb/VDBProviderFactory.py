from .providers import QdrantProvider
from .VDBEnums import VDBEnums
from controllers.BaseController import BaseController

class VDBProviderFactory:
    def __init__(self, config):
        self.config = config
        self.base_controller = BaseController()

    def create(self, provider: str):
        
        if provider == VDBEnums.QDRANT.value:
            return QdrantProvider(db_path= self.base_controller.get_db_path(self.config.VECTOR_DB_PATH), distance_method= self.config.DISTANCE_METHOD)
        
        return None