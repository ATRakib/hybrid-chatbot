from pydantic import BaseModel
from typing import List, Optional

class ChatMessage(BaseModel):
    message: str

class ChatResponse(BaseModel):
    response: str
    sources: List[dict] = []

class TrainRequest(BaseModel):
    table_name: str

class TrainResponse(BaseModel):
    message: str
    processed_rows: int