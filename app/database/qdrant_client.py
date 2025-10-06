from qdrant_client import QdrantClient
from qdrant_client.http.models import Distance, VectorParams, PointStruct
from app.config import settings
import os

class QdrantService:
    _client = None
    
    @classmethod
    def get_client(cls):
        if cls._client is None:
            # Create qdrant storage directory if not exists
            storage_path = "./qdrant_storage"
            os.makedirs(storage_path, exist_ok=True)
            cls._client = QdrantClient(path=storage_path)
        return cls._client
    
    def __init__(self):
        self.client = self.get_client()
        self.collection_name = settings.COLLECTION_NAME
    
    def create_collection(self, vector_size=1536):
        try:
            collections = self.client.get_collections()
            collection_names = [col.name for col in collections.collections]
            
            if self.collection_name not in collection_names:
                self.client.create_collection(
                    collection_name=self.collection_name,
                    vectors_config=VectorParams(size=vector_size, distance=Distance.COSINE)
                )
        except Exception as e:
            print(f"Collection create error: {e}")
    
    def upsert_points(self, points):
        try:
            self.client.upsert(
                collection_name=self.collection_name,
                points=points
            )
        except Exception as e:
            print(f"Upsert error: {e}")
    
    def search(self, query_vector, limit=5):
        try:
            collections = self.client.get_collections()
            collection_names = [col.name for col in collections.collections]
            
            if self.collection_name not in collection_names:
                raise ValueError(f"Collection {self.collection_name} not found")
                
            return self.client.search(
                collection_name=self.collection_name,
                query_vector=query_vector,
                limit=limit,
                with_payload=True
            )
        except Exception as e:
            print(f"Search error: {e}")
            raise ValueError(f"Collection {self.collection_name} not found")