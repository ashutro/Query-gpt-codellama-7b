# frontend/streamlit_app.py
import streamlit as st
import requests
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import json
from datetime import datetime
import time

# Page configuration
st.set_page_config(
    page_title="QueryGPT Local",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for better styling
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        color: #1f77b4;
        text-align: center;
        margin-bottom: 2rem;
    }
    .query-box {
        background-color: #f0f2f6;
        padding: 1rem;
        border-radius: 0.5rem;
        margin: 1rem 0;
    }
    .result-box {
        background-color: #ffffff;
        padding: 1rem;
        border-radius: 0.5rem;
        border: 1px solid #e0e0e0;
        margin: 1rem 0;
    }
    .sql-query {
        background-color: #1e1e1e;
        color: #ffffff;
        padding: 1rem;
        border-radius: 0.5rem;
        font-family: 'Courier New', monospace;
        margin: 1rem 0;
    }
</style>
""", unsafe_allow_html=True)

# Initialize session state
if 'query_history' not in st.session_state:
    st.session_state.query_history = []
if 'backend_url' not in st.session_state:
    st.session_state.backend_url = "http://localhost:8000"

def check_backend_health():
    """Check if backend service is running"""
    try:
        response = requests.get(f"{st.session_state.backend_url}/api/health", timeout=5)
        return response.status_code == 200
    except:
        return False

def get_database_schema():
    """Fetch database schema from backend"""
    try:
        response = requests.get(f"{st.session_state.backend_url}/api/schema", timeout=10)
        if response.status_code == 200:
            return response.json()['schema']
        return "Schema not available"
    except:
        return "Failed to fetch schema"

def execute_query(natural_query):
    """Send query to backend and return results"""
    try:
        payload = {
            "query": natural_query,
            "user_id": "streamlit_user"
        }
        
        response = requests.post(
            f"{st.session_state.backend_url}/api/query",
            json=payload,
            timeout=120  # Increased timeout for local LLM processing
        )
        
        if response.status_code == 200:
            return response.json()
        else:
            st.error(f"Backend error: {response.status_code} - {response.text}")
            return None
            
    except requests.exceptions.Timeout:
        st.error("Query timeout - the local AI model is taking too long to respond")
        return None
    except Exception as e:
        st.error(f"Connection error: {str(e)}")
        return None

def create_visualization(df, query_result):
    """Create appropriate visualization based on data"""
    if df.empty:
        return None
    
    # Simple heuristics for chart type selection
    numeric_columns = df.select_dtypes(include=['int64', 'float64']).columns.tolist()
    categorical_columns = df.select_dtypes(include=['object']).columns.tolist()
    
    if len(numeric_columns) >= 1 and len(categorical_columns) >= 1:
        # Bar chart for categorical vs numeric data
        fig = px.bar(
            df, 
            x=categorical_columns[0], 
            y=numeric_columns[0],
            title=f"{numeric_columns[0]} by {categorical_columns[0]}"
        )
        return fig
    elif len(numeric_columns) >= 2:
        # Scatter plot for numeric vs numeric
        fig = px.scatter(
            df,
            x=numeric_columns[0],
            y=numeric_columns[1],
            title=f"{numeric_columns[1]} vs {numeric_columns[0]}"
        )
        return fig
    
    return None

# Main interface
st.markdown('<h1 class="main-header">🤖 QueryGPT Local</h1>', unsafe_allow_html=True)
st.markdown("### Ask questions about your data in plain English!")

# Sidebar
with st.sidebar:
    st.header("🔧 System Status")
    
    # Backend health check
    if check_backend_health():
        st.success("✅ Backend Service Running")
    else:
        st.error("❌ Backend Service Offline")
        st.markdown("""
        **To start the backend:**
        ```
        cd ~/querygpt-local
        source venv/bin/activate
        python backend/app/main.py
        ```
        """)
    
    st.header("📊 Database Schema")
    with st.expander("View Schema", expanded=False):
        schema_info = get_database_schema()
        st.text(schema_info)
    
    st.header("💡 Example Queries")
    example_queries = [
        "Show me all customers from the USA",
        "What are the top 5 products by revenue?",
        "How many orders were completed last month?",
        "Which customers have spent the most money?",
        "What's the average order value by country?"
    ]
    
    for query in example_queries:
        if st.button(query, key=f"example_{hash(query)}"):
            st.session_state.current_query = query

# Main query interface
col1, col2 = st.columns([3, 1])

with col1:
    # Query input
    query_input = st.text_area(
        "Enter your question:",
        height=100,
        placeholder="e.g., Show me the top 10 customers by total spending",
        value=st.session_state.get('current_query', '')
    )

with col2:
    st.write("")  # Spacing
    st.write("")  # Spacing
    execute_button = st.button("🚀 Execute Query", type="primary", use_container_width=True)

# Process query
if execute_button and query_input.strip():
    with st.spinner("🤖 Processing your query with local AI..."):
        result = execute_query(query_input.strip())
        
        if result:
            # Store in history
            st.session_state.query_history.append({
                'timestamp': datetime.now(),
                'query': query_input.strip(),
                'result': result
            })
            
            # Display results
            st.markdown("---")
            st.markdown("## 📊 Query Results")
            
            # SQL Query
            st.markdown("### Generated SQL Query:")
            st.code(result['sql_query'], language='sql')
            
            st.markdown("### Explanation:") 
            st.markdown(result['explanation'])
            
            # Results table
            if result['results']:
                st.markdown(f"### Results ({result['row_count']} rows):")
                df = pd.DataFrame(result['results'])
                st.dataframe(df, use_container_width=True)
                
                # Visualization
                fig = create_visualization(df, result)
                if fig:
                    st.markdown("### Visualization:")
                    st.plotly_chart(fig, use_container_width=True)
                
                # Download option
                csv = df.to_csv(index=False)
                st.download_button(
                    label="📥 Download CSV",
                    data=csv,
                    file_name=f"query_results_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                    mime="text/csv"
                )
            else:
                st.info("No results found for your query.")
            
            # Performance info
            st.markdown(f"**Execution Time:** {result['execution_time']:.2f} seconds")

# Query History
if st.session_state.query_history:
    st.markdown("---")
    st.markdown("## 📝 Query History")
    
    for i, entry in enumerate(reversed(st.session_state.query_history[-5:])):  # Show last 5
        with st.expander(f"🕐 {entry['timestamp'].strftime('%H:%M:%S')} - {entry['query'][:50]}..."):
            st.code(entry['result']['sql_query'], language='sql')
            if entry['result']['results']:
                st.dataframe(pd.DataFrame(entry['result']['results']))

# Clear history button
if st.session_state.query_history:
    if st.button("🗑️ Clear History"):
        st.session_state.query_history = []
        st.experimental_rerun()

# Footer
st.markdown("---")
st.markdown("""
<div style='text-align: center; color: #666;'>
    <p></p>
    <p>QueryGPT Local - Powered by Ollama CodeLlama on Local</p>
    <p>Built with ❤️ using FastAPI, Streamlit, and SQLite</p>
    <p>Built by 👷🏽‍♂️<a href='https://www.linkedin.com/in/ashutro' target='_blank'>ashutro</a></p>
</div>
""", unsafe_allow_html=True)
