import pyodbc
from app.config import settings

class MSSQLConnection:
    def __init__(self):
        self.connection_string = settings.DB_CONNECTION_STRING
    
    def get_connection(self):
        return pyodbc.connect(self.connection_string)
    
    def get_tables(self):
        conn = self.get_connection()
        cursor = conn.cursor()
        try:
            cursor.execute("SELECT TABLE_NAME FROM INFORMATION_SCHEMA.TABLES WHERE TABLE_TYPE = 'BASE TABLE'")
            tables = [row[0] for row in cursor.fetchall()]
            return tables
        finally:
            conn.close()
    
    def get_columns(self, table_name):
        conn = self.get_connection()
        cursor = conn.cursor()
        try:
            # SQL Injection থেকে বাঁচার জন্য parameterized query
            cursor.execute(
                "SELECT COLUMN_NAME, DATA_TYPE FROM INFORMATION_SCHEMA.COLUMNS WHERE TABLE_NAME = ?",
                (table_name,)
            )
            columns = [(row[0], row[1]) for row in cursor.fetchall()]
            return columns
        finally:
            conn.close()
    
    def get_table_data(self, table_name):
        conn = self.get_connection()
        cursor = conn.cursor()
        try:
            # Table name validation করা (SQL injection থেকে বাঁচতে)
            cursor.execute(
                "SELECT TABLE_NAME FROM INFORMATION_SCHEMA.TABLES WHERE TABLE_NAME = ? AND TABLE_TYPE = 'BASE TABLE'",
                (table_name,)
            )
            if not cursor.fetchone():
                raise ValueError(f"Table {table_name} does not exist")
            
            cursor.execute(f"SELECT * FROM [{table_name}]")
            columns = [desc[0] for desc in cursor.description]
            column_types = [desc[1] for desc in cursor.description]
            rows = cursor.fetchall()
            return columns, column_types, rows
        finally:
            conn.close()