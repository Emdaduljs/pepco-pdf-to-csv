import streamlit as st
import pandas as pd
import os
import fitz  # PyMuPDF
import pdfplumber
import pytesseract
from PIL import Image
import re
import io

st.set_page_config(page_title="Smart PDF Data Merger", layout="wide")
st.title("📑 Merge Excel with PDF (Text + Tables + Scans)")

# --- Load Excel File ---
st.sidebar.header("1. Select Preloaded Excel")
excel_files = [f for f in os.listdir("data") if f.endswith((".xlsx", ".csv"))]
selected_file = st.sidebar.selectbox("Choose a file:", excel_files)

if selected_file:
    path = os.path.join("data", selected_file)
    df = pd.read_excel(path) if selected_file.endswith(".xlsx") else pd.read_csv(path)
    st.subheader("📊 Original Excel Data")
    st.dataframe(df, use_container_width=True)
else:
    st.warning("No Excel files found in /data.")
    st.stop()

# --- Upload PDF ---
st.sidebar.header("2. Upload PDF")
uploaded_pdf = st.sidebar.file_uploader("Upload any type of PDF", type="pdf")

# --- Helper: Extract fields from text (PyMuPDF or OCR) ---
def extract_fields(text):
    fields = {
        "Customer Name": r"Customer Name:\s*(.+)",
        "Account Number": r"Account Number:\s*(\d+)",
        "Billing Period": r"Billing Period:\s*(.+)",
        "Total Usage (kWh)": r"Total Usage:\s*([\d,\.]+)\s*kWh",
        "Service Address": r"Service Address:\s*(.+)"
    }
    results = {}
    for field, pattern in fields.items():
        match = re.search(pattern, text)
        results[field] = match.group(1).strip() if match else "Not Found"
    return results

# --- Helper: Try extracting tables ---
def extract_table_data(pdf_path):
    table_text = ""
    with pdfplumber.open(pdf_path) as pdf:
        for page in pdf.pages:
            tables = page.extract_tables()
            for table in tables:
                df_table = pd.DataFrame(table[1:], columns=table[0])
                table_text += df_table.to_csv(index=False)
    return table_text

# --- Helper: OCR extraction from scanned PDFs ---
def extract_ocr_text(pdf_path):
    doc = fitz.open(pdf_path)
    full_text = ""
    for i, page in enumerate(doc):
        pix = page.get_pixmap(dpi=300)
        img = Image.open(io.BytesIO(pix.tobytes("png")))
        text = pytesseract.image_to_string(img)
        full_text += text
    return full_text

# --- PDF Processing Logic ---
if uploaded_pdf:
    with open("temp_upload.pdf", "wb") as f:
        f.write(uploaded_pdf.read())
    st.sidebar.success("✅ PDF uploaded.")

    try:
        # Try extracting text using PyMuPDF
        doc = fitz.open("temp_upload.pdf")
        pdf_text = "\n".join([page.get_text() for page in doc])
        extracted_fields = extract_fields(pdf_text)
        if "Not Found" in extracted_fields.values():
            raise ValueError("Text too sparse. Trying OCR...")
        method = "📝 Text Extraction (PyMuPDF)"
    except:
        # Fallback to OCR for scanned PDFs
        pdf_text = extract_ocr_text("temp_upload.pdf")
        extracted_fields = extract_fields(pdf_text)
        method = "🧠 OCR Extraction (Tesseract)"

    # Try extracting tables with pdfplumber
    try:
        table_data_csv = extract_table_data("temp_upload.pdf")
        table_df = pd.read_csv(io.StringIO(table_data_csv))
        st.subheader("📄 Table Extracted from PDF (if any)")
        st.dataframe(table_df, use_container_width=True)
    except:
        table_df = None

    # Display extracted fields
    st.subheader(f"🔍 Extracted Fields ({method})")
    st.json(extracted_fields)

    # Add to main DataFrame
    for key, value in extracted_fields.items():
        df[key] = value

    st.subheader("📦 Final Merged Data")
    st.dataframe(df, use_container_width=True)

    st.download_button("⬇️ Download CSV", df.to_csv(index=False), "merged_data.csv", "text/csv")
else:
    st.info("Upload a PDF to extract and merge.")
