import streamlit as st
import pandas as pd
import os
import fitz  # PyMuPDF
import pdfplumber
import pytesseract
from pdf2image import convert_from_bytes
from PIL import Image
import re
import io

# === Configure Tesseract executable path (update if your path differs) ===
pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\tesseract-5.5.1\tesseract.exe"

# === Streamlit page config ===
st.set_page_config(page_title="Smart PDF Data Merger", layout="wide")
st.title("📑 Merge Excel with PDF (Text + Tables + Scans)")

# === Load Excel File ===
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

# === Upload PDF ===
st.sidebar.header("2. Upload PDF")
uploaded_pdf = st.sidebar.file_uploader("Upload any type of PDF", type="pdf")

# === Extract fields by regex from text ===
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

# === Extract tables from PDF using pdfplumber ===
def extract_table_data(pdf_path):
    table_text = ""
    with pdfplumber.open(pdf_path) as pdf:
        for page in pdf.pages:
            tables = page.extract_tables()
            for table in tables:
                df_table = pd.DataFrame(table[1:], columns=table[0])
                table_text += df_table.to_csv(index=False)
    return table_text

# === OCR extraction from scanned PDF pages ===
def extract_ocr_text(pdf_path):
    doc = fitz.open(pdf_path)
    full_text = ""
    for page in doc:
        pix = page.get_pixmap(dpi=300)
        img = Image.open(io.BytesIO(pix.tobytes("png")))
        text = pytesseract.image_to_string(img)
        full_text += text
    return full_text

# === Convert PDF bytes to images via pdf2image for OCR fallback ===
def ocr_from_pdf_bytes(pdf_bytes, poppler_path):
    images = convert_from_bytes(pdf_bytes, poppler_path=poppler_path)
    full_text = ""
    for img in images:
        text = pytesseract.image_to_string(img)
        full_text += text
    return full_text

# === Main PDF processing ===
if uploaded_pdf:
    # Save uploaded PDF temporarily
    temp_pdf_path = "temp_upload.pdf"
    with open(temp_pdf_path, "wb") as f:
        f.write(uploaded_pdf.read())
    st.sidebar.success("✅ PDF uploaded.")

    # Step 1: Try text extraction with PyMuPDF
    try:
        doc = fitz.open(temp_pdf_path)
        pdf_text = "\n".join([page.get_text() for page in doc])
        extracted_fields = extract_fields(pdf_text)
        if "Not Found" in extracted_fields.values():
            raise ValueError("Missing some fields — falling back to OCR")
        method = "📝 Text Extraction (PyMuPDF)"
    except Exception:
        # Step 2: OCR fallback with PyMuPDF rendered images + Tesseract
        pdf_text = extract_ocr_text(temp_pdf_path)
        extracted_fields = extract_fields(pdf_text)
        method = "🧠 OCR Extraction (Tesseract via PyMuPDF)"

        # If fields still missing, try pdf2image OCR fallback (if poppler installed)
        if "Not Found" in extracted_fields.values():
            try:
                pdf_bytes = open(temp_pdf_path, "rb").read()
                poppler_path = r"C:\Program Files\poppler-24.08.0\Library\bin"  # update if needed
                pdf_text = ocr_from_pdf_bytes(pdf_bytes, poppler_path)
                extracted_fields = extract_fields(pdf_text)
                method = "🧠 OCR Extraction (Tesseract via pdf2image + Poppler)"
            except Exception as e:
                st.warning(f"PDF2Image OCR failed: {e}")

    # Step 3: Extract tables with pdfplumber
    try:
        table_data_csv = extract_table_data(temp_pdf_path)
        if table_data_csv.strip():
            table_df = pd.read_csv(io.StringIO(table_data_csv))
            st.subheader("📄 Table Extracted from PDF (if any)")
            st.dataframe(table_df, use_container_width=True)
        else:
            table_df = None
    except Exception:
        table_df = None

    # Show extracted fields
    st.subheader(f"🔍 Extracted Fields ({method})")
    st.json(extracted_fields)

    # Merge extracted fields into original DataFrame as new columns (same value for all rows)
    for key, value in extracted_fields.items():
        df[key] = value

    st.subheader("📦 Final Merged Data")
    st.dataframe(df, use_container_width=True)

    # Download CSV button
    csv_bytes = df.to_csv(index=False).encode("utf-8")
    st.download_button("⬇️ Download Merged CSV", csv_bytes, "merged_data.csv", "text/csv")

else:
    st.info("Upload a PDF to extract and merge.")

