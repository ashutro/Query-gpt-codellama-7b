

# 🧠 QueryGPT Local

**QueryGPT Local** is an offline-powered tool that converts natural language questions into executable SQL queries using a locally running LLM via [Ollama](https://ollama.com). It runs on a lightweight FastAPI backend, executes the generated SQL against a local **SQLite** database, and returns results along with explanations — perfect for local data exploration, learning, or prototyping.

---

## 🚀 Features

- 🔍 Converts natural language to SQL using **CodeLlama** (or any local model supported by Ollama)
- 🛡️ Safe execution of **only SELECT** queries
- 🧠 Returns SQL query, result rows, and a natural-language explanation
- ⚡ Built with **FastAPI** — quick and modern Python API
- 🧱 Works entirely **offline** (no OpenAI or external APIs required)
- 📄 Dynamic schema extraction and sample data preview
- 🧪 Optional frontend via **Streamlit**

---

## 📂 Project Structure

```
querygpt-local/
│
├── backend/
│   ├── app/
│   │   └── main.py         # FastAPI app logic
│   └── database/
│       └── querygpt.db     # SQLite DB with tables and sample data
│
├── frontend/               # (Optional: Streamlit UI)
│
└── README.md
```

---

## 🧰 Tech Stack

- **Backend**: [FastAPI](https://fastapi.tiangolo.com/)
- **LLM**: [Ollama](https://ollama.com/) (`codellama:7b`, `llama3`, etc.)
- **Database**: SQLite (easy to use and file-based)
- **Language**: Python 3.8+

---

## ⚙️ Setup Instructions

To get started with QueryGPT Local, follow these steps to set up your environment. You'll install and launch Ollama with a local LLM, set up the Python backend, and run the FastAPI server locally.

### ✅ Step 1: Clone the Repository

```bash
git clone https://github.com/your-username/Query-gpt-codellama-7b.git
cd Query-gpt-codellama-7b
```

### ✅ Step 2: Install and Start Ollama

1. Install [Ollama](https://ollama.com/download) on your system  
2. Download a model (e.g. `codellama:7b`):

```bash
ollama run codellama:7b
```

This will start the Ollama server at `http://localhost:11434`.

### ✅ Step 3: Set Up Python Backend

```bash
cd backend
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

> Make sure the `requirements.txt` file exists in the `backend/` directory.

### ✅ Step 4: Start the Backend Server

```bash
uvicorn app.main:app --reload
```

Once the server is running, you can test it using `curl`, Postman, or a frontend UI like Streamlit. Navigate to `http://localhost:8000/docs` for the interactive Swagger API docs.

API will be running at: `http://localhost:8000`

---

## 🔌 API Endpoints

| Method | Endpoint         | Description                                |
|--------|------------------|--------------------------------------------|
| GET    | `/api/health`    | Health check of the backend                |
| GET    | `/api/schema`    | Get current SQLite schema with sample data |
| POST   | `/api/query`     | Submit a natural language query            |

### Example POST `/api/query`

```json
{
  "query": "Show top 5 products by revenue"
}
```

**Response:**

```json
{
  "sql_query": "SELECT product_name, SUM(quantity * unit_price) AS revenue FROM orders GROUP BY product_name ORDER BY revenue DESC LIMIT 5;",
  "results": [...],
  "explanation": "This query calculates revenue by multiplying quantity with unit price...",
  "row_count": 5,
  "execution_time": 0.023
}
```

## 📥 Downloading Final Result

Once your natural language query is processed and the SQL query is executed, you can download the results in various formats. You can integrate this feature using Streamlit or add a button in your frontend to export:

- **CSV**: Export tabular results as `.csv` file
- **JSON**: Export raw API response
- **TXT**: Save query explanation and SQL query for reference

> In Streamlit, you can use `st.download_button()` to let users download results:

```python
st.download_button(
    label="Download Result as CSV",
    data=csv_data,
    file_name='query_results.csv',
    mime='text/csv',
)
```

---

## 📊 Example Use Case

**Input Query:**  
> "List all completed orders from active customers placed in July."

**Generated SQL:**  
```sql
SELECT * FROM orders
JOIN customers ON orders.customer_id = customers.id
WHERE customers.is_active = 1
AND orders.status = 'completed'
AND strftime('%m', orders.order_date) = '07';
```

---

## 🖥️ Optional: Streamlit Frontend

You can connect the backend with a simple Streamlit UI to send queries from a webpage.

```bash
cd frontend
streamlit run app.py
```

Make sure the backend (`uvicorn`) is running on port `8000`.

---

## 📜 License

This project is open-sourced under the **MIT License**. Feel free to use, modify, and share.

---

## 🤝 Contributing

- 💡 Found a bug? Open an (https://github.com/your-username/Query-gpt-codellama-7b/issues)
- 🌟 Star the repo to support
- 📬 PRs welcome!

---

## 👤 Author

**Ashutosh Kumar**  
[GitHub](https://github.com/ashutro) | [LinkedIn](https://www.linkedin.com/in/ashutro)

---

## 🧠 Bonus: Tips for Custom Models

Want to use your own model? Just update this line inside `main.py`:

```python
"model": "codellama:7b"
```

Replace with any model you’ve downloaded locally via Ollama.

---

**Build SQL from your thoughts – run offline, learn more.** 🚀