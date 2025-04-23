# -*- coding: utf-8 -*-
"""
Created on Tue Apr 22 11:15:22 2025

@author: HP
"""

import re
import pandas as pd
from datetime import datetime
from langchain.schema import Document

def extract_all_lease_records(docs, apartment_name=None):
    all_records = []
    for doc in docs:
        text = doc.page_content
        filename = doc.metadata.get("source", "")

        doc_apartment = ""
        match1 = re.search(r'described as: (.*?)\s*\("?Premises"?\)', text, re.IGNORECASE)
        if match1:
            doc_apartment = match1.group(1).strip().lower()

        if apartment_name:
            ap_key = re.sub(r'[^a-z0-9]', '', apartment_name.lower().rstrip('s'))
            doc_apartment_check = re.sub(r'[^a-z0-9]', '', filename.lower())
            if ap_key not in doc_apartment_check:
                continue

        lease_dates = re.search(
            r"commence on (?:the )?(\d{1,2}(?:st|nd|rd|th)? day of \w+, \d{4}).*?(?:until|through|ending on).*?(\d{1,2}(?:st|nd|rd|th)? day of \w+, \d{4})",
            text, re.IGNORECASE | re.DOTALL
        )
        if not lease_dates:
            continue

        def convert_to_mmddyyyy(date_str):
            try:
                date_obj = datetime.strptime(date_str, "%dth day of %B, %Y")
            except ValueError:
                date_obj = datetime.strptime(re.sub(r"(st|nd|rd|th)", "", date_str), "%d day of %B, %Y")
            return date_obj.strftime("%m-%d-%Y")

        unit = re.search(r"(?:Apartment|Unit|Flat)\s*(?:number)?\s*[:\-]?\s*(\d+)", text, re.IGNORECASE)
        if not unit:
            continue

        floor_match = re.search(
            r"(?:floor\s*(\d+)|(?:located on|situated on|on the)\s*(\d+)(?:st|nd|rd|th)?\s*floor)",
            text, re.IGNORECASE
        )
        floor = floor_match.group(1) or floor_match.group(2) if floor_match else ""

        # Tenant Name
        tenant_match = re.search(r'Tenant.*?["“](\w+[^"\n\r]*)["”]?', text, re.IGNORECASE)
        tenant = tenant_match.group(1).strip() if tenant_match else ""

        # Landlord Location (ex: 2900 clear springs dr New York 34550)
        landlord_match = re.search(r'located at\s*\(?["“]?([^"\n\r]+)', text, re.IGNORECASE)
        landlord_location = landlord_match.group(1).strip() if landlord_match else ""

        # City from Property Address
        city_match = re.search(r'situated in\s+([^,]+),\s+([A-Za-z ]+),\s+\d{5}', text, re.IGNORECASE)
        city = city_match.group(1).strip() if city_match else ""

        record = {
            "Apartment": doc_apartment.title(),
            "Unit/Apartment Number": unit.group(1),
            "Floor": floor,
            "Start Date": convert_to_mmddyyyy(lease_dates.group(1)),
            "End Date": convert_to_mmddyyyy(lease_dates.group(2)),
            "Status": re.search(r"\b(Occupied|Vacant|Unoccupied|Leased)\b", text, re.IGNORECASE).group(1).capitalize()
                      if re.search(r"\b(Occupied|Vacant|Unoccupied|Leased)\b", text, re.IGNORECASE) else "Occupied",
            "Tenant Name": tenant,
            "Landlord Location": landlord_location,
            "City": city
        }

        rent = re.search(r"pay \$([\d,]+) rent per month", text, re.IGNORECASE)
        if rent:
            record["Monthly Rent"] = f"${rent.group(1)}"

        all_records.append(record)

    return pd.DataFrame(all_records) if all_records else pd.DataFrame()
