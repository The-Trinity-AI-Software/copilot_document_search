# -*- coding: utf-8 -*-
"""
Created on Sun Apr 20 15:57:31 2025

@author: HP
"""

import os
import fitz  # PyMuPDF
import docx
import json
import pandas as pd

BASE_DIR = os.path.dirname(os.path.abspath(__file__))


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


def save_results_as_json(df, path):
    try:
        df_copy = df.copy()
        df_copy = df_copy.applymap(lambda x: float(x) if isinstance(x, (int, float)) else str(x))
        with open(path, "w", encoding="utf-8") as f:
            json.dump(df_copy.to_dict(orient="records"), f, indent=2, ensure_ascii=False)
    except Exception as e:
        print(f"Error saving JSON: {e}")


def save_results_as_excel(df, path):
    try:
        df.to_excel(path, index=False)
    except Exception as e:
        print(f"Error saving Excel: {e}")
def save_uploaded_files(uploaded_files, upload_folder):
    filepaths = []
    os.makedirs(upload_folder, exist_ok=True)
    for file in uploaded_files:
        file_path = os.path.join(upload_folder, file.filename)
        file.save(file_path)
        filepaths.append(file_path)
    return filepaths


def prepare_documents(filepaths):
    documents = []
    for path in filepaths:
        try:
            text = extract_text(path)
            documents.append({"filename": os.path.basename(path), "content": text})
        except Exception as e:
            print(f"Failed to process {path}: {e}")
    return pd.DataFrame(documents)
