from ..VDBInterface import VDBInterface
from ..VDBEnums import VDBEnums, DistanceMethodEnums
import logging
from qdrant_client import QdrantClient, models
import numpy as np
from models.db_schemes import RetrievedDocument
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
        results = self.client.query_points(
            collection_name=collection_name,
            query=query_vector.tolist(),
            limit=top_k,
            with_payload= True
        )
        

        if not results:
            return None
        
        documents = []
        for point in results.points:
            payload = point.payload

            # Access the correct field
            texts = payload.get("texts")

            # Handle list-or-string cases
            if isinstance(texts, list):
                text = "".join(texts)
            else:
                text = texts  # string

            documents.append(
                RetrievedDocument(
                    text=text,
                    score=point.score,
                )
            )

        return documents

"""

(id=0,
 version=0,
   score=0.6377312087487774,
     payload=
        {'texts':
             [
                'Evolution is the change in the heritable',
                'heritable characteristics of biological',
                'populations over successive generations.',
                'It occurs when evolutionary processes such as',
                'such as genetic drift and natural selection act',
                'act on genetic variation, resulting in certain',
                'certain characteristics becoming more or less',
                'or less common within a population over',
                'over successive generations.',
                'The process of evolution has given rise to', 'rise to biodiversity at every level of biological',
                'organisation.',
                'The scientific theory of evolution by natural',
                'natural selection was conceived independently by',
                'by two British naturalists, Charles Darwin and',
                'and Alfred Russel Wallace, in the mid-19th',
                'mid-19th century as an explanation for why',
                'for why organisms are adapted to their physical',
                'physical and biological environments.',
                'The theory was first set out in detail in',
                "detail in Darwin's book On the Origin of Species.",
                'Species.', 'Evolution by natural selection is established by',
                'by observable facts about living organisms: more',
                'more offspring are often produced than can',
                'than can possibly survive;',
                'traits vary among individuals with respect to',
                'to their morphology, physiology, and behaviour;',
                'different traits confer different rates of',
                'rates of survival and reproduction (differential',
                'fitness); and traits can be passed from',
                'from generation to generation (heritability of',
                'of fitness).', 'In successive generations, members of a',
                'of a population are therefore more likely to be',
                'to be replaced by the offspring of parents with',
                'with favourable characteristics for that',
                'for that environment.'
             ], 
         'metadata': {'source': '/mnt/d/Side-Projects/mini-rag/src/assets/files/1/itfcdq6cd6u4_texttest.txt'}}, vector=None, shard_key=None, order_value=None)

"""