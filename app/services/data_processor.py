from app.database.mssql_connection import MSSQLConnection
from app.database.qdrant_client import QdrantService
from app.services.embeddings_service import EmbeddingsService
from qdrant_client.models import PointStruct
import uuid
import pyodbc

class DataProcessor:
    def __init__(self):
        self.mssql = MSSQLConnection()
        self.qdrant = QdrantService()
        self.embeddings = EmbeddingsService()
    
    def get_default_value(self, column_type):
        """Data type অনুসারে default value return করবে"""
        column_type = str(column_type).lower()
        
        # Numeric types
        if any(t in column_type for t in ['int', 'decimal', 'numeric', 'float', 'real', 'money']):
            return "0"
        
        # Date/Time types
        if any(t in column_type for t in ['date', 'time', 'datetime']):
            return "1900-01-01"
        
        # Boolean types
        if 'bit' in column_type:
            return "0"
        
        # String types (varchar, nvarchar, text, char, etc.)
        return "N/A"
    
    def clean_and_format_value(self, value, column_type):
        """Value clean করবে এবং null হলে default value দিবে"""
        if value is None or str(value).strip() == '':
            return self.get_default_value(column_type)
        
        # Value কে string এ convert করে clean করবে
        cleaned_value = str(value).strip()
        
        # Multiple spaces কে single space এ convert করবে
        cleaned_value = ' '.join(cleaned_value.split())
        
        return cleaned_value
    
    def process_table_data(self, table_name):
        try:
            columns, column_types, rows = self.mssql.get_table_data(table_name)
        except ValueError as e:
            raise ValueError(f"Invalid table: {str(e)}")
        
        self.qdrant.create_collection()
        
        points = []
        skipped_rows = 0
        
        for i, row in enumerate(rows):
            row_data = {}
            text_parts = []
            
            for j, col in enumerate(columns):
                # Value clean করে নিব
                cleaned_value = self.clean_and_format_value(row[j], column_types[j])
                row_data[col] = cleaned_value
                
                # Text content এ শুধু meaningful data যুক্ত করবে
                # if cleaned_value and cleaned_value != "N/A" and not self.is_numeric_type(column_types[j]):
                if cleaned_value and cleaned_value != "N/A":
                    text_parts.append(f"{col}: {cleaned_value}")
            
            # যদি কোনো meaningful data না থাকে তাহলে skip করবে
            # if not text_parts:
            #     skipped_rows += 1
            #     continue
            
            text_content = " | ".join(text_parts)
            
            try:
                embedding = self.embeddings.get_embedding(text_content)
                
                point = PointStruct(
                    id=str(uuid.uuid4()),
                    vector=embedding,
                    payload={
                        "table_name": table_name,
                        "columns": columns,
                        "data": row_data,
                        "text_content": text_content,
                        "row_index": i
                    }
                )
                points.append(point)
            except Exception as e:
                print(f"Row {i} embedding error: {e}")
                skipped_rows += 1
                continue
        
        if points:
            self.qdrant.upsert_points(points)
        
        print(f"Total processed: {len(points)}, Skipped: {skipped_rows}")
        return len(points)
    
    def process_sql_query_data(self, sql_query, source_name):
        """SQL query execute করে data train করার method"""
        conn = self.mssql.get_connection()
        cursor = conn.cursor()
        
        try:
            cursor.execute(sql_query)
            columns = [desc[0] for desc in cursor.description]
            column_types = [desc[1] for desc in cursor.description]
            rows = cursor.fetchall()
            
            self.qdrant.create_collection()
            
            points = []
            skipped_rows = 0
            
            for i, row in enumerate(rows):
                row_data = {}
                text_parts = []
                
                for j, col in enumerate(columns):
                    cleaned_value = self.clean_and_format_value(row[j], column_types[j])
                    row_data[col] = cleaned_value
                    
                    # if cleaned_value and cleaned_value != "N/A" and not self.is_numeric_type(column_types[j]):
                    if cleaned_value and cleaned_value != "N/A":
                        text_parts.append(f"{col}: {cleaned_value}")
                
                # if not text_parts:
                #     skipped_rows += 1
                #     continue
                
                text_content = " | ".join(text_parts)
                
                try:
                    embedding = self.embeddings.get_embedding(text_content)
                    
                    point = PointStruct(
                        id=str(uuid.uuid4()),
                        vector=embedding,
                        payload={
                            "source_name": source_name,
                            "columns": columns,
                            "data": row_data,
                            "text_content": text_content,
                            "sql_query": sql_query,
                            "row_index": i
                        }
                    )
                    points.append(point)
                except Exception as e:
                    print(f"Row {i} embedding error: {e}")
                    skipped_rows += 1
                    continue
            
            if points:
                self.qdrant.upsert_points(points)
            
            print(f"Total processed: {len(points)}, Skipped: {skipped_rows}")
            return len(points)
            
        except pyodbc.Error as e:
            raise ValueError(f"SQL execution error: {str(e)}")
        finally:
            conn.close()

    def is_numeric_type(self, column_type):    
        """Check if column type is numeric"""    
        column_type = str(column_type).lower()    
        return any(t in column_type for t in ['int', 'decimal', 'numeric', 'float', 'real', 'money'])