import os
import fitz
import docx
import re
from datetime import datetime
from dateutil import parser
from langchain.schema import Document

def extract_apartment_name(text):
    lines = text.splitlines()[:30]
    for line in lines:
        clean_line = line.strip()
        if any(word in clean_line.lower() for word in ["apartment", "residence", "tower", "block"]):
            name_match = re.search(r'\b([A-Za-z\s]+(?:Apartment|Residence|Tower|Block))\b', clean_line, re.IGNORECASE)
            if name_match:
                return name_match.group(1).strip().title()
    return "Not Found"

def extract_flat_number(text):
    match = re.search(r'(Apartment|Flat|Unit)\s+(No\.?|Number)?\s*[:\-]?\s*(\d+)', text, re.IGNORECASE)
    if match:
        return match.group(3).strip()
    return "Not Found"

from dateutil import parser

def extract_lease_start_date(text):
    text = re.sub(r'\s+', ' ', text)  # <<< important fix → clean text
    patterns = [
        r'commence(?:s|d)?\s+on\s+(?:the\s+)?(\d{1,2}(?:st|nd|rd|th)?\s+day of\s+\w+,\s+\d{4})',
        r'start(?:s|ed)?\s+on\s+(?:the\s+)?(\d{1,2}(?:st|nd|rd|th)?\s+day of\s+\w+,\s+\d{4})',
        r'effective\s+from\s+(?:the\s+)?(\d{1,2}(?:st|nd|rd|th)?\s+day of\s+\w+,\s+\d{4})'
    ]
    for pat in patterns:
        match = re.search(pat, text, re.IGNORECASE)
        if match:
            raw_date = match.group(1).strip()
            try:
                dt = parser.parse(raw_date, fuzzy=True)
                return dt.strftime("%m-%d-%Y")
            except:
                continue
    return "Not Found"

def extract_lease_end_date(text):
    text = re.sub(r'\s+', ' ', text)  # <<< important fix → clean text
    patterns = [
        r'(?:until|end(?:s|ed)?|terminate(?:s|d)?)\s+(?:its\s+end\s+at\s+)?(?:\d{1,2}:\d{2}\s*[APMapm\.]*\s+on\s+)?(?:the\s+)?(\d{1,2}(?:st|nd|rd|th)?\s+day of\s+\w+,\s+\d{4})'
    ]
    for pat in patterns:
        match = re.search(pat, text, re.IGNORECASE)
        if match:
            raw_date = match.group(1).strip()
            try:
                dt = parser.parse(raw_date, fuzzy=True)
                return dt.strftime("%m-%d-%Y")
            except:
                continue
    return "Not Found"


def extract_status(start_date, end_date):
    try:
        end_dt = datetime.strptime(end_date, "%m-%d-%Y")
        today = datetime.today()
        return "Active" if end_dt >= today else "Expired"
    except:
        return "Unknown"

def extract_all_fields(text):
    start_date = extract_lease_start_date(text)
    end_date = extract_lease_end_date(text)

    return {
        "Apartment Name": extract_apartment_name(text),
        "Flat Number": extract_flat_number(text),
        "Start Date": start_date,
        "End Date": end_date,
        "Status": extract_status(start_date, end_date),
    }

def extract_text(file_path):
    ext = os.path.splitext(file_path)[1].lower()
    if ext == ".pdf":
        return extract_text_from_pdf(file_path)
    elif ext == ".docx":
        return extract_text_from_docx(file_path)
    elif ext == ".txt":
        return extract_text_from_txt(file_path)
    raise ValueError("Unsupported file type")

def extract_text_from_pdf(pdf_path):
    text = ""
    doc = fitz.open(pdf_path)
    for page in doc:
        text += page.get_text()
    doc.close()
    return text

def extract_text_from_docx(docx_path):
    text = ""
    doc = docx.Document(docx_path)
    for para in doc.paragraphs:
        text += para.text + "\n"
    return text

def extract_text_from_txt(txt_path):
    with open(txt_path, "r", encoding="utf-8") as f:
        return f.read()
    
FIELD_MAPPING = {
    "apartment": "Apartment Name",
    "apartment name": "Apartment Name",
    "apartment number": "Flat Number",
    "flat": "Flat Number",
    "flat number": "Flat Number",
    "unit": "Flat Number",
    "unit number": "Flat Number",
    "start date": "Start Date",
    "end date": "End Date",
    "last date": "End Date",
    "status": "Status",
    "tenant": "Tenant Name",
    "tenant name": "Tenant Name",
    "rent": "Rent Amount",
    "monthly rent": "Rent Amount",
    "late fee": "Late Fee",
    "security deposit": "Security Deposit",
    "pet": "Pet Policy",
    "pet policy": "Pet Policy"
}

def get_requested_fields_from_prompt(prompt):
    prompt = prompt.lower()
    requested_fields = []

    for key, value in FIELD_MAPPING.items():
        if key in prompt:
            requested_fields.append(value)

    return list(set(requested_fields)) if requested_fields else list(FIELD_MAPPING.values())
