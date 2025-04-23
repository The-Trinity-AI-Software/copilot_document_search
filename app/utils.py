# -*- coding: utf-8 -*-
"""
Created on Sun Apr 20 15:57:31 2025

@author: HP
"""

# utils.py (Updated: includes get_requested_fields_from_prompt)
import os
import fitz  # PyMuPDF
import docx
import re
from langchain.schema import Document

# === Field Mapping Dictionary ===
FIELD_MAPPING = {
    "unit": "Unit/Apartment Number",
    "unit number": "Unit/Apartment Number",
    "apartment number": "Unit/Apartment Number",
    "floor": "Floor",
    "start date": "Start Date",
    "end date": "End Date",
    "status": "Status",
    "tenant name": "Tenant Name",
    "monthly rent": "Monthly Rent",
    "rent": "Monthly Rent",
    "apartment": "Apartment"
}

def get_requested_fields_from_prompt(prompt):
    prompt = prompt.lower()
    requested_fields = []

    for key, value in FIELD_MAPPING.items():
        if key in prompt:
            requested_fields.append(value)

    return list(set(requested_fields)) if requested_fields else list(FIELD_MAPPING.values())

def extract_text(file_path):
    ext = os.path.splitext(file_path)[1].lower()
    if ext == ".pdf":
        return extract_text_from_pdf(file_path)
    elif ext == ".docx":
        return extract_text_from_docx(file_path)
    elif ext == ".txt":
        return extract_text_from_txt(file_path)
    else:
        raise ValueError("Unsupported file type")

def extract_text_from_pdf(pdf_path):
    text = ""
    try:
        doc = fitz.open(pdf_path)
        for page in doc:
            text += page.get_text()
        doc.close()
    except Exception as e:
        print(f"Error reading PDF: {e}")
    return text

def extract_text_from_docx(docx_path):
    text = ""
    try:
        doc = docx.Document(docx_path)
        for para in doc.paragraphs:
            text += para.text + "\n"
    except Exception as e:
        print(f"Error reading DOCX: {e}")
    return text

def extract_text_from_txt(txt_path):
    try:
        with open(txt_path, "r", encoding="utf-8") as f:
            return f.read()
    except Exception as e:
        print(f"Error reading TXT: {e}")
        return ""

def load_uploaded_documents(upload_dir):
    documents = []
    for filename in os.listdir(upload_dir):
        filepath = os.path.join(upload_dir, filename)
        if os.path.isfile(filepath):
            ext = os.path.splitext(filename)[1].lower()
            if ext in [".pdf", ".docx", ".txt"]:
                text = extract_text(filepath)
                documents.append(Document(page_content=text, metadata={"source": filename}))
    return documents