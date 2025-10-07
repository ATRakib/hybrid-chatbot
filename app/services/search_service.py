from app.database.qdrant_client import QdrantService
from app.services.embeddings_service import EmbeddingsService

class SearchService:
    def __init__(self):
        self.qdrant = QdrantService()
        self.embeddings = EmbeddingsService()
    
    def search_and_respond(self, query):
        query_embedding = self.embeddings.get_embedding(query)
        
        try:
            search_results = self.qdrant.search(query_embedding)
        except ValueError:
            # Collection not found, return default message
            return "দুঃখিত, কোনো ডেটা ট্রেইন করা হয়নি। প্রথমে ডেটা ট্রেইন করুন।", []
        
        context_parts = []
        sources = []
        
        for result in search_results:
            payload = result.payload
            context_parts.append(payload["text_content"])
            
            source_info = {
                "data": payload.get("data", {}),
                "score": result.score
            }
            
            if "table_name" in payload:
                source_info["source"] = payload["table_name"]
            
            if "source_name" in payload:
                source_info["source"] = payload["source_name"]
            
            sources.append(source_info)
        
        context = "\n\n".join(context_parts)
        
        if not context.strip():
            return "দুঃখিত, আপনার প্রশ্নের উত্তর খুঁজে পাইনি।", []
        
        response = self.embeddings.get_chat_response(query, context)
        
        return response, sources