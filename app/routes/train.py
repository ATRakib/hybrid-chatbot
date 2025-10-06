from fastapi import APIRouter, HTTPException
from app.models.schemas import TrainRequest, TrainResponse
from app.services.data_processor import DataProcessor
from app.database.mssql_connection import MSSQLConnection
from app.database.qdrant_client import QdrantService

router = APIRouter()
data_processor = DataProcessor()
mssql = MSSQLConnection()
qdrant = QdrantService()

@router.get("/tables")
async def get_tables():
    try:
        tables = mssql.get_tables()
        return {"tables": tables}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")

@router.get("/tables/{table_name}/columns")
async def get_columns(table_name: str):
    try:
        columns = mssql.get_columns(table_name)
        # শুধু column names return করবে (data types frontend এ দরকার নেই)
        column_names = [col[0] for col in columns]
        return {"columns": column_names}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")

@router.post("/train", response_model=TrainResponse)
async def train_data(request: TrainRequest):
    try:
        processed_rows = data_processor.process_table_data(request.table_name)
        
        if processed_rows == 0:
            return TrainResponse(
                message=f"Warning: No valid data found in {request.table_name}",
                processed_rows=0
            )
        
        return TrainResponse(
            message=f"Successfully trained {processed_rows} rows from {request.table_name}",
            processed_rows=processed_rows
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Training failed: {str(e)}")

@router.post("/train-sql")
async def train_sql_query(request: dict):
    """SQL query দিয়ে data train করার endpoint"""
    sql_query = request.get("sql_query")
    source_name = request.get("source_name")
    
    if not sql_query:
        raise HTTPException(status_code=400, detail="SQL query is required")
    
    if not source_name:
        raise HTTPException(status_code=400, detail="Source name is required")
    
    try:
        points_count = data_processor.process_sql_query_data(sql_query, source_name)
        
        if points_count == 0:
            return {
                "message": "Warning: No valid data found from SQL query",
                "count": 0
            }
        
        return {
            "message": f"Successfully trained {points_count} data points from {source_name}",
            "count": points_count
        }
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Training failed: {str(e)}")

@router.get("/debug/collection-info")
async def get_collection_info():
    try:
        collections = qdrant.client.get_collections()
        collection_names = [col.name for col in collections.collections]
        
        if qdrant.collection_name in collection_names:
            info = qdrant.client.get_collection(qdrant.collection_name)
            count = qdrant.client.count(qdrant.collection_name)
            return {
                "collection_exists": True,
                "collection_name": qdrant.collection_name,
                "points_count": count.count,
                "vector_size": info.config.params.vectors.size,
                "distance": info.config.params.vectors.distance
            }
        else:
            return {
                "collection_exists": False,
                "available_collections": collection_names
            }
    except Exception as e:
        return {"error": str(e)}

@router.get("/debug/sample-data")
async def get_sample_data():
    try:
        collections = qdrant.client.get_collections()
        collection_names = [col.name for col in collections.collections]
        
        if qdrant.collection_name not in collection_names:
            return {"error": "Collection not found"}
        
        # Get first 3 points to show metadata
        results = qdrant.client.scroll(
            collection_name=qdrant.collection_name,
            limit=3,
            with_payload=True
        )
        
        sample_data = []
        for point in results[0]:
            sample_data.append({
                "id": point.id,
                "payload": point.payload
            })
        
        return {
            "sample_count": len(sample_data),
            "sample_data": sample_data
        }
    except Exception as e:
        return {"error": str(e)}