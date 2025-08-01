import streamlit as st
import pdfplumber
import pandas as pd
import pytesseract
from pdf2image import convert_from_bytes
from io import BytesIO
import tempfile
import os

st.set_page_config(page_title="📄 PDF Table Extractor - Custom Headers")

st.title("📄 PDF Table Extractor - Custom Headers")
st.caption("Upload PDF file with the table")

uploaded_file = st.file_uploader("Upload PDF", type=["pdf"])

# Define expected headers
expected_headers = [
    "Order - ID",
    "Item No",
    "Supplier product code",
    "Colour",
    "6/9", "9/12", "12/18", "18/24", "24/36",
    "Bar Code"
]

def extract_with_pdfplumber(pdf_bytes):
    data_rows = []
    try:
        with pdfplumber.open(BytesIO(pdf_bytes)) as pdf:
            for page in pdf.pages:
                tables = page.extract_tables()
                for table in tables:
                    for row in table:
                        clean_row = [cell.strip() if isinstance(cell, str) else "" for cell in row]
                        if any("Order" in str(cell) for cell in clean_row):
                            continue  # Skip header-like rows
                        if len(clean_row) >= 10:
                            data_rows.append(clean_row[:10])
    except Exception as e:
        st.error(f"pdfplumber extraction error: {e}")
    return data_rows

def extract_with_ocr(pdf_bytes):
    data_rows = []
    try:
        images = convert_from_bytes(pdf_bytes)
        for image in images:
            text = pytesseract.image_to_string(image)
            lines = text.split("\n")
            for line in lines:
                parts = [p.strip() for p in line.split() if p.strip()]
                if len(parts) >= 10:
                    data_rows.append(parts[:10])
    except Exception as e:
        st.error(f"OCR extraction error: {e}")
    return data_rows

def build_dataframe(rows):
    df = pd.DataFrame(rows, columns=expected_headers[:len(rows[0])])
    return df

if uploaded_file:
    pdf_bytes = uploaded_file.read()
    
    st.info("🔍 Trying to extract table from PDF...")

    rows = extract_with_pdfplumber(pdf_bytes)

    if not rows:
        st.warning("❌ No table found with `pdfplumber`. Trying OCR fallback...")
        rows = extract_with_ocr(pdf_bytes)

    if not rows:
        st.error("No valid data found in PDF text or OCR.")
    else:
        df = build_dataframe(rows)
        st.success(f"✅ Extracted {len(df)} rows.")

        st.dataframe(df)

        csv_data = df.to_csv(index=False).encode('utf-8')
        st.download_button(
            label="📥 Download CSV",
            data=csv_data,
            file_name="extracted_table.csv",
            mime="text/csv"
        )
