from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import sqlite3
import requests
import json
import re
from typing import Dict, List, Any
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="QueryGPT Local", version="1.0.0")

# Add CORS middleware for frontend communication
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:8501"],  # Streamlit default port
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class QueryRequest(BaseModel):
    query: str
    user_id: str = "default"

class QueryResponse(BaseModel):
    sql_query: str
    results: List[Dict[str, Any]]
    explanation: str
    row_count: int
    execution_time: float

class QueryGPTEngine:
    def __init__(self, db_path: str = "database/querygpt.db"):
        self.db_path = db_path
        self.ollama_url = "http://localhost:11434/api/generate"
        self.schema_info = self._get_schema_info()
    
    def _get_schema_info(self) -> str:
        """Extract database schema information"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Get all tables
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        tables = cursor.fetchall()
        
        schema_description = "Database Schema:\n\n"
        
        for (table_name,) in tables:
            schema_description += f"Table: {table_name}\n"
            
            # Get column information
            cursor.execute(f"PRAGMA table_info({table_name});")
            columns = cursor.fetchall()
            
            for col in columns:
                col_name, col_type, not_null, default_val, pk = col[1], col[2], col[3], col[4], col[5]
                schema_description += f"  - {col_name} ({col_type})"
                if pk:
                    schema_description += " [PRIMARY KEY]"
                if not_null:
                    schema_description += " [NOT NULL]"
                schema_description += "\n"
            
            # Get sample data
            cursor.execute(f"SELECT * FROM {table_name} LIMIT 3;")
            sample_data = cursor.fetchall()
            if sample_data:
                schema_description += f"  Sample data: {sample_data[0]}\n"
            
            schema_description += "\n"
        
        conn.close()
        return schema_description
    
    def _generate_sql_with_ollama(self, natural_query: str) -> str:
        """Generate SQL using local Ollama model"""
        prompt = f"""You are a SQL expert. Convert the following natural language query to SQL.

{self.schema_info}

Business Rules:
- Use proper joins between tables
- Always include meaningful column aliases
- For revenue calculations, multiply quantity by unit_price
- Active customers have is_active = 1
- Completed orders have status = 'completed'

Natural Language Query: {natural_query}

Generate only the SQL query, no explanations. The query should be valid SQLite syntax.

SQL Query:"""

        payload = {
            "model": "codellama:7b",
            "prompt": prompt,
            "stream": False,
            "options": {
                "temperature": 0.1,
                "top_p": 0.9,
                "num_ctx": 2048
            }
        }
        
        try:
            response = requests.post(self.ollama_url, json=payload, timeout=60)
            response.raise_for_status()
            
            result = response.json()
            generated_text = result['response']
            
            # Extract SQL query from response
            sql_query = self._extract_sql_query(generated_text)
            return sql_query
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Error calling Ollama API: {e}")
            raise HTTPException(status_code=500, detail="Failed to generate SQL query")
    
    def _extract_sql_query(self, text: str) -> str:
        """Extract clean SQL query from generated text"""
        # Remove common prefixes and clean up
        text = text.strip()
        text = re.sub(r"```[\s\S]*?```", lambda m: m.group(0).replace("```", "").strip(), text)
        
        # Look for SQL keywords to find the start of the query
        sql_keywords = ['SELECT', 'WITH', 'INSERT', 'UPDATE', 'DELETE']
        
        lines = text.split('\n')
        sql_lines = []
        found_sql = False
        
        for line in lines:
            line = line.strip()
            if not found_sql:
                # Check if line starts with SQL keyword
                if any(line.upper().startswith(keyword) for keyword in sql_keywords):
                    found_sql = True
                    sql_lines.append(line)
            else:
                # Continue collecting SQL lines
                if line and not line.startswith('--') and not line.startswith('#'):
                    sql_lines.append(line)
                elif not line:  # Empty line might indicate end of SQL
                    break
        
        sql_query = ' '.join(sql_lines)
        
        # Clean up common issues
        sql_query = re.sub(r';+$', ';', sql_query)  # Remove multiple semicolons
        sql_query = sql_query.strip()

        # Auto-convert non-SQLite functions to SQLite-compatible syntax
        sql_query = re.sub(r"(?i)\bYEAR\s*\(\s*([^)]+?)\s*\)", r"strftime('%Y', \1)", sql_query)
        sql_query = re.sub(r"(?i)\bMONTH\s*\(\s*([^)]+?)\s*\)", r"strftime('%m', \1)", sql_query)
        sql_query = re.sub(r"(?i)\bDAY\s*\(\s*([^)]+?)\s*\)", r"strftime('%d', \1)", sql_query)
        sql_query = re.sub(r"(?i)\bNOW\s*\(\s*\)", r"CURRENT_TIMESTAMP", sql_query)
        sql_query = re.sub(r"(?i)\bCURDATE\s*\(\s*\)", r"DATE('now')", sql_query)
        sql_query = re.sub(r"(?i)\bGETDATE\s*\(\s*\)", r"CURRENT_TIMESTAMP", sql_query)
        
        if not sql_query:
            sql_query = text  # Fallback to original text
        
        return sql_query
    
    def _execute_sql_query(self, sql_query: str) -> tuple:
        """Execute SQL query against SQLite database"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row  # Enable column access by name
        cursor = conn.cursor()
        
        try:
            # Security check - only allow SELECT statements
            if not sql_query.strip().upper().startswith('SELECT'):
                raise ValueError("Only SELECT queries are allowed")
            def sanitize_sql(sql_query: str) -> str:
                sql_query = sql_query.strip()
                # Only keep the first statement (before first ;)
                if ";" in sql_query:
                    sql_query = sql_query.split(";")[0]
                return sql_query
        
            sql_query_sanitized = sanitize_sql(sql_query)
            cursor.execute(sql_query_sanitized)
            rows = cursor.fetchall()
            
            # Convert to list of dictionaries
            results = [dict(row) for row in rows]
            
            return results, len(results)
            
        except Exception as e:
            logger.error(f"SQL execution error: {e}")
            raise HTTPException(status_code=400, detail=f"SQL execution failed: {str(e)}")
        
        finally:
            conn.close()
    
    def _generate_explanation(self, natural_query: str, sql_query: str, results: List[Dict]) -> str:
        """Generate a plain-text explanation of the query and results (no markdown code block)"""
        explanation = f"I converted your question '{natural_query}' into the following SQL query:\n\n"
        explanation += sql_query + "\n\n"
        explanation += f"This query returned {len(results)} rows.\n"
        if results:
            explanation += "It likely selects, filters, and aggregates data as per your question.\n"
        return explanation
    
    async def process_query(self, natural_query: str) -> QueryResponse:
        """Main method to process natural language query"""
        import time
        start_time = time.time()
        
        try:
            # Generate SQL using Ollama
            sql_query = self._generate_sql_with_ollama(natural_query)
            
            # Execute the query
            results, row_count = self._execute_sql_query(sql_query)
            
            # Generate explanation
            explanation = self._generate_explanation(natural_query, sql_query, results)
            
            execution_time = time.time() - start_time
            
            return QueryResponse(
                sql_query=sql_query,
                results=results,
                explanation=explanation,
                row_count=row_count,
                execution_time=execution_time
            )
            
        except Exception as e:
            logger.error(f"Query processing error: {e}")
            raise HTTPException(status_code=500, detail=str(e))

# Initialize the query engine
query_engine = QueryGPTEngine()

@app.post("/api/query", response_model=QueryResponse)
async def process_query(request: QueryRequest):
    """Process natural language query and return SQL results"""
    return await query_engine.process_query(request.query)

@app.get("/api/schema")
async def get_schema():
    """Return database schema information"""
    return {"schema": query_engine.schema_info}

@app.get("/api/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "timestamp": "2024-01-01T00:00:00Z"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
