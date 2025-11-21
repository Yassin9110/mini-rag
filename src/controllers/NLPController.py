from . import BaseController
from models.db_schemes import Project, DataChunk
from typing import List
import json

class NLPController(BaseController):

    def __init__(self, vectordb_client, generation_client, embedding_client):
        super().__init__()

        self.vectordb_client = vectordb_client
        self.generation_client = generation_client
        self.embedding_client = embedding_client

    def create_collection_name(self, project_id: str):
        return f"collection_{project_id}".strip()
    
    def reset_vdb_collection(self, project: Project):
        collection_name = self.create_collection_name(project.id)
        self.vectordb_client.delete_collection(collection_name)

    def get_vdb_collection_info(self, project: Project):
        collection_name = self.create_collection_name(project.id)
        collection_info = self.vectordb_client.get_collection_info(collection_name)

        return json.loads(json.dumps(collection_info, default= lambda x: x.__dict__))

    def index_into_vdb(self, project: Project, chunks: List[DataChunk],
                       chunks_ids: List[int],
                       do_reset: bool = False):

        # step1: get collection name
        collection_name = self.create_collection_name(project.id)

        # step2: manage items
        texts = [c.chunk_text for c in chunks]
        metadatas = [c.metadata for c in chunks]
        vectors = [ self.embedding_client.embed_text(text) for text in texts ]
        # step3: create collection
        self.vectordb_client.create_collection(collection_name = collection_name, vector_size =self.embedding_client.embedding_dim ,do_reset = do_reset)

        # step: insert into vector_db
        _ = self.vectordb_client.insert_many(collection_name = collection_name, texts = texts, vectors = vectors, metadatas = metadatas, ids = chunks_ids)

        return True


    def search_vectordb_collection(self, project: Project, text: str, top_k: int = 10):
        # step1: get collection name
        collection_name = self.create_collection_name(project.id)

        # step2: get text embedding vector
        vector = self.embedding_client.embed_text(text)

        if not vector or len(vector) == 0:
            return False
        # step3: do semantic search
        result = self.vectordb_client.search_by_vector(collection_name = collection_name, query_vector = vector, top_k = top_k)
        if not result:
            return False
        return json.loads(json.dumps(result, default= lambda x: x.__dict__))
