# 🧠 CoPilot Document Search

This application allows you to upload documents (PDF, DOCX, TXT) and perform intelligent LLM-based document search using semantic, keyword, and structured matching.

## 🔧 Setup

```bash
pip install -r requirements.txt


copilot_docsearch/
├── app/
│   ├── __init__.py
│   ├── utils.py              # Utility functions for document parsing, searching
│   |── search_engine.py
    |--- lease_extraction.py
     # Logic for LLM / semantic search / keyword match
│
├── templates/
│   └── index.html           # (Optional) custom CSS
│
├── uploads/                  # Uploaded user documents (PDF, DOCX, TXT)
├── output/                   # Stores output Excel and JSON files
│
├          
├── main.py                    # Flask backend if needed (API mode)
├── requirements.txt
├── README.md
