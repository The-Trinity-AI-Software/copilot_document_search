from flask import Flask, request, jsonify, send_file, render_template
import os
import json
from datetime import datetime
import pandas as pd
from app.utils import extract_all_fields, extract_text, get_requested_fields_from_prompt
from app.search_engine import SearchEngine
import re

UPLOAD_FOLDER = "uploads"
UPLOAD_LOG = "uploaded_files.json"
EXCEL_FOLDER = "excel"
JSON_FOLDER = "json"

os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(EXCEL_FOLDER, exist_ok=True)
os.makedirs(JSON_FOLDER, exist_ok=True)

app = Flask(__name__)
search_engine = SearchEngine()

loaded_files = []
apartment_names = []

@app.before_first_request
def load_documents():
    global loaded_files, apartment_names
    if os.path.exists(UPLOAD_LOG):
        with open(UPLOAD_LOG, "r") as f:
            loaded_files = json.load(f)
    else:
        loaded_files = []

    current_files = set(os.listdir(UPLOAD_FOLDER))
    loaded_files = list(current_files.intersection(set(loaded_files)))

    with open(UPLOAD_LOG, "w") as f:
        json.dump(loaded_files, f)

    docs = []
    apartment_names.clear()

    for file in loaded_files:
        path = os.path.join(UPLOAD_FOLDER, file)
        text = extract_text(path)
        fields = extract_all_fields(text)

        apartment = fields.get("Apartment Name", "")
        if apartment and apartment != "Not Found" and apartment not in apartment_names:
            apartment_names.append(apartment)

        docs.append(text)

    if docs:
        search_engine.prepare_documents(docs)

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/upload", methods=["POST"])
def upload_files():
    global loaded_files

    files = request.files.getlist("files[]")
    for file in files:
        filename = file.filename
        save_path = os.path.join(UPLOAD_FOLDER, filename)

        file.save(save_path)

        if filename not in loaded_files:
            loaded_files.append(filename)

    with open(UPLOAD_LOG, "w") as f:
        json.dump(loaded_files, f)

    return jsonify({"message": "✅ Files loaded / updated successfully!"})

def detect_apartment_name_dynamic(query):
    query_lower = query.lower()
    for apartment in apartment_names:
        if apartment.lower() in query_lower:
            return apartment.lower()
    return None

@app.route("/search", methods=["POST"])
def search():
    query = request.form.get("query")
    mode = request.form.get("search_mode")

    results = []
    apartment_filter = detect_apartment_name_dynamic(query)
    requested_attributes = get_requested_fields_from_prompt(query)

    if "Apartment Name" not in requested_attributes:
        requested_attributes.insert(0, "Apartment Name")

    flat_match = re.search(r'(flat|unit|apartment)\s*(\d+)', query.lower())
    query_flat_number = flat_match.group(2) if flat_match else None

    matched_any = False

    for file in loaded_files:
        path = os.path.join(UPLOAD_FOLDER, file)
        text = extract_text(path)
        fields = extract_all_fields(text)

        doc_apartment_name = fields.get("Apartment Name", "").lower()

        if doc_apartment_name == "not found" and apartment_filter:
            fields["Apartment Name"] = apartment_filter.title() + " Apartment"
            doc_apartment_name = apartment_filter

        if apartment_filter:
            if apartment_filter in doc_apartment_name:
                matched_any = True
                if query_flat_number:
                    if fields.get("Flat Number", "").lower() == query_flat_number:
                        results.append({attr: fields.get(attr, "") for attr in requested_attributes})
                else:
                    results.append({attr: fields.get(attr, "") for attr in requested_attributes})
        else:
            results.append({attr: fields.get(attr, "") for attr in requested_attributes})

    if apartment_filter and not matched_any:
        results.append({attr: "" for attr in requested_attributes})

    return jsonify(results)


@app.route("/download_json", methods=["POST"])
def download_json():
    data = request.get_json()
    timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
    json_path = os.path.join(JSON_FOLDER, f"results_{timestamp}.json")

    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=4)

    return send_file(json_path, as_attachment=True)

@app.route("/download_excel", methods=["POST"])
def download_excel():
    data = request.get_json()
    timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
    excel_path = os.path.join(EXCEL_FOLDER, f"results_{timestamp}.xlsx")

    df = pd.DataFrame(data)
    df.to_excel(excel_path, index=False)

    return send_file(excel_path, as_attachment=True)

if __name__ == "__main__":
    app.run(debug=True, port=8086)
