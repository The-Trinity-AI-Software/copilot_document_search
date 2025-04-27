# -*- coding: utf-8 -*-
"""
Created on Sun Apr 20 16:00:55 2025

@author: HP
"""


from flask import Flask, request, render_template, send_file, session
import os
import pandas as pd
from datetime import datetime
from app.utils import extract_text, load_uploaded_documents, get_requested_fields_from_prompt
from app.lease_extraction import extract_all_lease_records
from langchain.schema import Document

app = Flask(__name__)
app.secret_key = "lease_secret_ravi_2025"

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
UPLOAD_DIR = os.path.join(BASE_DIR, "uploads")
EXPORT_BASE_DIR = "G:/MVP/mnt/data/copilot_document_search/output"
EXCEL_EXPORT_DIR = os.path.join(EXPORT_BASE_DIR, "excel")
JSON_EXPORT_DIR = os.path.join(EXPORT_BASE_DIR, "json")

os.makedirs(UPLOAD_DIR, exist_ok=True)
os.makedirs(EXCEL_EXPORT_DIR, exist_ok=True)
os.makedirs(JSON_EXPORT_DIR, exist_ok=True)

@app.route("/")
def index():
    return render_template("index.html", results=None, download_links=None)

@app.route("/upload", methods=["POST"])
def upload():
    if "file" not in request.files:
        return render_template("index.html", results="\u26a0\ufe0f No file uploaded.")
    
    file = request.files["file"]
    save_path = os.path.join(UPLOAD_DIR, file.filename)
    file.save(save_path)

    session["uploaded_file_path"] = save_path
    return render_template("index.html", results=f"✅ Uploaded: {file.filename}")

@app.route("/search", methods=["GET"])
def search():
    uploaded_file_path = session.get("uploaded_file_path")
    if not uploaded_file_path or not os.path.exists(uploaded_file_path):
        return render_template("index.html", results="❌ No uploaded file found. Please upload a document first.")

    query = request.args.get("query", "")
    if not query:
        return render_template("index.html", results="\u26a0\ufe0f Please enter a query.")

    text = extract_text(uploaded_file_path)
    doc = Document(page_content=text, metadata={"source": os.path.basename(uploaded_file_path)})
    df = extract_all_lease_records([doc])

    if df.empty:
        return render_template("index.html", results="❌ No lease records found.")

    requested_fields = get_requested_fields_from_prompt(query)
    available_fields = [f for f in requested_fields if f in df.columns]
    filtered_df = df[available_fields] if available_fields else df

    apt_name = df["Apartment"].iloc[0].replace(" ", "_") if "Apartment" in df.columns and not df.empty else "lease_output"
    today = datetime.now().strftime("%Y%m%d")
    excel_filename = f"{apt_name}_{today}.xlsx"
    json_filename = f"{apt_name}_{today}.json"
    excel_path = os.path.join(EXCEL_EXPORT_DIR, excel_filename)
    json_path = os.path.join(JSON_EXPORT_DIR, json_filename)

    filtered_df.to_excel(excel_path, index=False)
    filtered_df.to_json(json_path, orient="records", indent=2)

    session["excel_path"] = excel_path
    session["json_path"] = json_path

    return render_template(
        "index.html",
        results=filtered_df.to_html(classes="table", index=False, border=0),
        download_links={
            "json": "/download/json",
            "excel": "/download/excel"
        }
    )
@app.route("/download/excel")
def download_excel():
    path = session.get("excel_path")
    if path and os.path.exists(path):
        return send_file(path, as_attachment=True)
    return "Excel file not found.", 404

@app.route("/download/json")
def download_json():
    path = session.get("json_path")
    if path and os.path.exists(path):
        return send_file(path, as_attachment=True)
    return "JSON file not found.", 404

if __name__ == "__main__":
    app.run(debug=True, port=8086)
