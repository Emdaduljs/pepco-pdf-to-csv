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
        "Order - ID": r"Order\s*-\s*ID[:\s]*([^\n\r]+)",
        "Item No": r"Item\s*No[:\s]*([^\n\r]+)",
        "Supplier product code": r"Supplier\s*product\s*code[:\s]*([^\n\r]+)",
        "Colour": r"Colour[:\s]*([^\n\r]+)",
        "6/9": r"6/9[:\s]*([^\n\r]+)",
        "9/12": r"9/12[:\s]*([^\n\r]+)",
        "12/18": r"12/18[:\s]*([^\n\r]+)",
        "18/24": r"18/24[:\s]*([^\n\r]+)",
        "24/36": r"24/36[:\s]*([^\n\r]+)",
    }
    results = {}
    for field, pattern in fields.items():
        match = re.search(pattern, text)
        results[field] = match.group(1).strip() if match else "Not Found"
    return results

# --- Helper: Try extracting tables ---
def extract_table_data(pdf_file):
    table_text = ""
    with pdfplumber.open(pdf_file) as pdf:
        for page in pdf.pages:
            tables = page.extract_tables()
            for table in tables:
                df_table = pd.DataFrame(table[1:], columns=table[0])
                table_text += df_table.to_csv(index=False)
    return table_text

# --- Helper: OCR extraction from scanned PDFs (Local only) ---
def extract_ocr_text(pdf_file):
    try:
        doc = fitz.open(pdf_file)
        full_text = ""
        for i, page in enumerate(doc):
            pix = page.get_pixmap(dpi=300)
            img = Image.open(io.BytesIO(pix.tobytes("png")))
            # Make sure pytesseract is set up correctly
            text = pytesseract.image_to_string(img)
            full_text += text
        return full_text
    except pytesseract.pytesseract.TesseractNotFoundError:
        st.error("Tesseract OCR is not installed or not found on your system. OCR extraction won't work here.")
        return ""
    except Exception as e:
        st.error(f"OCR extraction failed: {e}")
        return ""

# --- PDF Processing Logic ---
if uploaded_pdf:
    temp_pdf_path = "temp_upload.pdf"
    with open(temp_pdf_path, "wb") as f:
        f.write(uploaded_pdf.read())
    st.sidebar.success("✅ PDF uploaded.")

    try:
        # Try extracting text using PyMuPDF
        doc = fitz.open(temp_pdf_path)
        pdf_text = "\n".join([page.get_text() for page in doc])
        extracted_fields = extract_fields(pdf_text)
        if "Not Found" in extracted_fields.values():
            raise ValueError("Text too sparse. Trying OCR fallback...")
        method = "📝 Text Extraction (PyMuPDF)"
    except Exception:
        # OCR fallback only works if running locally with Tesseract installed
        pdf_text = extract_ocr_text(temp_pdf_path)
        if pdf_text.strip():
            extracted_fields = extract_fields(pdf_text)
            method = "🧠 OCR Extraction (Tesseract)"
        else:
            extracted_fields = {k: "Not Found" for k in ["Customer Name", "Account Number", "Billing Period", "Total Usage (kWh)", "Service Address"]}
            method = "❌ No usable text extracted"

    # Try extracting tables with pdfplumber
    try:
        table_data_csv = extract_table_data(temp_pdf_path)
        table_df = pd.read_csv(io.StringIO(table_data_csv)) if table_data_csv else None
        if table_df is not None:
            st.subheader("📄 Table Extracted from PDF (if any)")
            st.dataframe(table_df, use_container_width=True)
    except Exception as e:
        st.warning(f"Failed to extract table data: {e}")
        table_df = None

    # Display extracted fields
    st.subheader(f"🔍 Extracted Fields ({method})")
    st.json(extracted_fields)

    # Add to main DataFrame (broadcast single values to all rows)
    for key, value in extracted_fields.items():
        df[key] = value

    st.subheader("📦 Final Merged Data")
    st.dataframe(df, use_container_width=True)

    st.download_button("⬇️ Download CSV", df.to_csv(index=False), "merged_data.csv", "text/csv")
else:
    st.info("Upload a PDF to extract and merge.")
