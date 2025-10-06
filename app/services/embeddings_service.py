import openai
from app.config import settings

class EmbeddingsService:
    def __init__(self):
        openai.api_key = settings.OPENAI_API_KEY
        self.client = openai.OpenAI(api_key=settings.OPENAI_API_KEY)
    
    def get_embedding(self, text):
        response = self.client.embeddings.create(
            model="text-embedding-ada-002",
            input=text
        )
        return response.data[0].embedding
    
    # Available OpenAI Models:
    # text-embedding-ada-002     → 1536 dimensions (পুরানো)
    # text-embedding-3-small     → 1536 dimensions (নতুন, দ্রুত)
    # text-embedding-3-large     → 3072 dimensions (সবচেয়ে ভালো)

    def get_chat_response(self, query, context):
        messages = [
            {"role": "system", "content": "You are a helpful assistant. Answer based on the provided context."},
            {"role": "user", "content": f"Context: {context}\n\nQuestion: {query}"}
        ]
        
        response = self.client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=messages,
            temperature=0.7
        )
        
        return response.choices[0].message.content
    
    # models 
    # "gpt-3.5-turbo": "সস্তা, ভালো quality",
    # "gpt-4": "সেরা quality, দামি", 
    # "gpt-4-turbo": "দ্রুত + ভালো",
    # "gpt-3.5-turbo-16k": "বেশি context length"
