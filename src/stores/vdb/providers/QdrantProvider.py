from ..VDBInterface import VDBInterface
from ..VDBEnums import VDBEnums, DistanceMethodEnums
import logging
from qdrant_client import QdrantClient, models
import numpy as np
from typing import List, Union

class QdrantProvider(VDBInterface):
    def __init__(self, db_path: str, distance_method):
        
        self.client = None
        self.db_path = db_path
        self.distance_method = None

        if distance_method == DistanceMethodEnums.COSINE.value:
            self.distance_method = models.Distance.COSINE
        elif distance_method == DistanceMethodEnums.DOT.value:
            self.distance_method == models.Distance.DOT

        self.logger = logging.getLogger(__name__)

    def connect(self):
        self.client = QdrantClient(path= self.db_path)

    def disconnect(self):
        self.client = None

    def is_collection_exists(self, collection_name):
        return self.client.collection_exists(collection_name)
    
    def list_collections(self)-> List:
        return self.client.get_collection()
    
    def get_collection_info(self, collection_name):
        return self.client.get_collection(collection_name)
    
    def delete_collection(self, collection_name):
        if self.is_collection_exists(collection_name):
            self.client.delete_collection(collection_name)
        else:
            self.logger.error("Collection doesn't exist to delete")

    def create_collection(self, collection_name, vector_size, do_reset = False):
        if do_reset:
            self.delete_collection(collection_name)
        
        if not self.is_collection_exists(collection_name):
            self.client.create_collection(collection_name= collection_name,
                                          vectors_config= models.VectorParams(size= vector_size, distance= self.distance_method))
            
            return True
        
        return False
    
    def insert_one(self, collection_name, text, vector, metadata, id = None):
        
        if not self.is_collection_exists(collection_name):
            self.logger.error("Can not insert new record to non existed collection")
            return False

        self.client.upsert(collection_name= collection_name,
                          points=[models.PointStruct(id= id, vector= vector, payload={ "text": text, "metadata": metadata})] 
                          )
        
        return True
    
    def insert_many(self, collection_name, texts, vectors, metadatas, ids, batch_size = 50):
        
        if metadatas is None:
            metadatas = [None] * len(texts)

        if ids is None:
            ids = list(range(0, len(texts)))

        for i in range(0, len(texts), batch_size):
            batch_end = i + batch_size

            batch_texts = texts[i:batch_end]
            batch_vectors = vectors[i:batch_end]
            batch_metadata = metadatas[i:batch_end]
            batch_ids = ids[i:batch_end]

            batch_records = [
                models.PointStruct(
                    id = batch_ids[x],
                    vector= batch_vectors[x], 
                    payload= {
                        "texts": batch_texts, "metadata": batch_metadata[x]
                    }
                )
                for x in range(len(batch_texts))
            ]

            self.client.upsert(collection_name= collection_name, points= batch_records)

        return True
    
    def search_by_vector(self, collection_name, query_vector, top_k=10):
        query_vector = np.array(query_vector).astype(np.float32)
        result = self.client.query_points(
            collection_name=collection_name,
            query=query_vector.tolist(),
            limit=top_k
        )

        return result

