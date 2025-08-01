import streamlit as st
import pdfplumber
import pytesseract
from pytesseract import Output
from pdf2image import convert_from_bytes
import pandas as pd
import tempfile
import os

# Ensure paths for Windows users
pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"
POPPLER_PATH = r"C:\Program Files\poppler-xx\Library\bin"  # Replace xx with version

st.set_page_config(page_title="PDF Table Extractor - Custom Headers", layout="wide")
st.title("📄 PDF Table Extractor - Custom Headers")

uploaded_file = st.file_uploader("Upload PDF file with the table", type=["pdf"])

if uploaded_file:
    st.success(f"Uploaded: {uploaded_file.name}")
    metadata = {}
    final_data = pd.DataFrame()

    with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp_file:
        tmp_file.write(uploaded_file.read())
        tmp_path = tmp_file.name

    def extract_with_pdfplumber(path):
        tables = []
        meta_text = []
        with pdfplumber.open(path) as pdf:
            for page in pdf.pages:
                text = page.extract_text()
                if text:
                    meta_text.append(text)
                table = page.extract_table()
                if table:
                    df = pd.DataFrame(table[1:], columns=table[0])
                    tables.append(df)
        return "\n".join(meta_text), tables

    def extract_with_ocr(path):
        if not os.environ.get("PATH", "").find(POPPLER_PATH) >= 0:
            os.environ["PATH"] += os.pathsep + POPPLER_PATH
        images = convert_from_bytes(open(path, 'rb').read())
        ocr_text = ""
        for img in images:
            text = pytesseract.image_to_string(img)
            ocr_text += text + "\n"
        return ocr_text

    def parse_metadata(text):
        lines = text.splitlines()
        for line in lines:
            if "Order No" in line:
                metadata["Order No"] = line.split(":")[-1].strip()
            if "Order Date" in line:
                metadata["Order Date"] = line.split(":")[-1].strip()
            if "Buyer" in line:
                metadata["Buyer"] = line.split(":")[-1].strip()
            if "Supplier" in line:
                metadata["Supplier"] = line.split(":")[-1].strip()
            if "Style" in line:
                metadata["Style"] = line.split(":")[-1].strip()

    st.markdown("🔍 Trying to extract table from PDF...")
    extracted_text, tables = extract_with_pdfplumber(tmp_path)

    if tables:
        st.success("✅ Table(s) extracted successfully from PDF!")
        for i, df in enumerate(tables):
            st.markdown(f"### Table {i + 1}")
            st.dataframe(df)
            final_data = pd.concat([final_data, df], ignore_index=True)
    else:
        st.warning("❌ No table found with pdfplumber. Trying OCR fallback...")
        try:
            extracted_text = extract_with_ocr(tmp_path)
            st.text_area("🔍 OCR Extracted Text", extracted_text, height=300)
        except Exception as e:
            st.error(f"OCR extraction error: {e}")

    if extracted_text:
        parse_metadata(extracted_text)
        if metadata:
            st.markdown("## 📌 Extracted Metadata")
            for k, v in metadata.items():
                st.write(f"**{k}:** {v}")
        else:
            st.warning("⚠️ Metadata not clearly found in text.")
    else:
        st.warning("⚠️ No valid data found in PDF text or OCR.")

    if not final_data.empty:
        st.markdown("## 📤 Export Data")
        csv = final_data.to_csv(index=False).encode('utf-8')
        st.download_button("📥 Download as CSV", csv, f"{uploaded_file.name}.csv", "text/csv")
    else:
        st.error("❌ No data rows extracted from PDF to append.")
