import streamlit as st
import pdfplumber
from pdf2image import convert_from_bytes
import pytesseract
from PIL import Image
import pandas as pd
import io

st.set_page_config(page_title="📄 PDF Table Extractor - Custom Headers", layout="wide")
st.title("📄 PDF Table Extractor - Custom Headers")

st.write("Upload PDF file with tables. If no tables are found, OCR fallback will try to extract text.")

uploaded_file = st.file_uploader("Upload PDF", type=["pdf"])

CUSTOM_HEADERS = [
    "Order - ID",
    "Item No",
    "Supplier product code",
    "Colour",
    "6/9",
    "9/12",
    "12/18",
    "18/24",
    "24/36",
]

def extract_tables_from_pdf(pdf_bytes):
    tables = []
    with pdfplumber.open(io.BytesIO(pdf_bytes)) as pdf:
        for page_number, page in enumerate(pdf.pages, start=1):
            page_tables = page.extract_tables()
            if page_tables:
                for t in page_tables:
                    tables.append(t)
    return tables

def ocr_pdf_tables(pdf_bytes):
    images = convert_from_bytes(pdf_bytes, dpi=300)
    all_text = ""
    for img in images:
        text = pytesseract.image_to_string(img)
        all_text += text + "\n"
    return all_text

def parse_text_to_table(text):
    # Simple heuristic: split lines and whitespace, may need customization
    lines = [line.strip() for line in text.splitlines() if line.strip()]
    rows = [line.split() for line in lines if line]  # crude split by whitespace
    return rows

if uploaded_file:
    pdf_bytes = uploaded_file.read()

    # Try pdfplumber tables first
    tables = extract_tables_from_pdf(pdf_bytes)
    if not tables:
        st.warning("No tables found using pdfplumber. Trying OCR fallback...")
        ocr_text = ocr_pdf_tables(pdf_bytes)
        rows = parse_text_to_table(ocr_text)
        if not rows:
            st.error("No tables found with OCR fallback either.")
        else:
            st.success(f"OCR extracted approx {len(rows)} rows.")
            df = pd.DataFrame(rows)
            st.dataframe(df)
    else:
        st.success(f"Found {len(tables)} tables with pdfplumber.")
        # For simplicity, use first table
        raw_table = tables[0]
        # Some rows might be uneven, normalize length
        max_cols = max(len(row) for row in raw_table)
        normalized_rows = [row + ['']*(max_cols - len(row)) for row in raw_table]

        # Create DataFrame with your custom headers if possible
        if len(CUSTOM_HEADERS) == max_cols:
            df = pd.DataFrame(normalized_rows[1:], columns=CUSTOM_HEADERS)
        else:
            df = pd.DataFrame(normalized_rows[1:], columns=normalized_rows[0])  # use first row as header

        st.dataframe(df)

    # Provide CSV download
    if 'df' in locals():
        csv_data = df.to_csv(index=False).encode('utf-8')
        st.download_button("⬇️ Download extracted table as CSV", csv_data, "extracted_table.csv", "text/csv")

else:
    st.info("Please upload a PDF file to begin.")

