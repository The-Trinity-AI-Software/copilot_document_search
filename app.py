# -*- coding: utf-8 -*-
"""
Created on Sun Apr 20 16:00:55 2025

@author: HP
"""

from flask import Flask, request, jsonify, render_template, send_file
import os
from utils.file_utils import extract_text, save_results_as_json, save_results_as_excel
from app.search_engine import SemanticSearchEngine

app = Flask(__name__)

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
UPLOAD_DIR = os.path.join(BASE_DIR, "uploads")
DOC_DIR = os.path.join(BASE_DIR, "processed")
os.makedirs(UPLOAD_DIR, exist_ok=True)
os.makedirs(DOC_DIR, exist_ok=True)

search_engine = SemanticSearchEngine()  # ✅ removed index_dir

# Utility: Save uploaded files
def save_uploaded_files(files, upload_dir):
    saved = []
    for file in files:
        path = os.path.join(upload_dir, file.filename)
        file.save(path)
        saved.append(path)
    return saved

# Utility: Prepare documents
def prepare_documents(paths):
    docs = []
    for path in paths:
        try:
            content = extract_text(path)
            docs.append({"file_path": path, "text": content})
        except Exception as e:
            print(f"❌ Failed to process {path}: {e}")
    return docs

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/upload", methods=["POST"])
def upload():
    if "files[]" not in request.files:
        return jsonify({"error": "No files provided"}), 400
    files = request.files.getlist("files[]")
    saved_paths = save_uploaded_files(files, UPLOAD_DIR)
    docs = prepare_documents(saved_paths)
    search_engine.docs = docs
    search_engine.embeddings = search_engine.model.encode([doc["text"] for doc in docs], convert_to_tensor=True)
    return jsonify({"message": f"{len(docs)} documents processed and indexed."})

@app.route("/query", methods=["POST"])
def query():
    data = request.json
    question = data.get("question")
    if not question:
        return jsonify({"error": "Missing query parameter"}), 400

    results = search_engine.search(question)
    return jsonify({
        "question": question,
        "results": [{"text": r[0], "score": round(r[1], 4)} for r in results]
    })


