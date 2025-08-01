import streamlit as st
import pandas as pd
import os
import io
import re
from PyPDF2 import PdfReader
from pdf2image import convert_from_bytes
import pytesseract

st.set_page_config(page_title="PEPCO PDF to CSV", layout="wide")
st.title("📄 PEPCO PDF to CSV Converter")

# --- Load Excel Data ---
excel_files = [f for f in os.listdir("data") if f.endswith((".xlsx", ".csv"))]

if not excel_files:
    st.error("No Excel files found in /data folder.")
    st.stop()

selected = st.selectbox("Select Excel file to merge:", excel_files)
df_excel = pd.read_excel(os.path.join("data", selected)) if selected.endswith(".xlsx") else pd.read_csv(os.path.join("data", selected))

# --- Upload PDF ---
uploaded = st.file_uploader("Upload PEPCO PDF", type="pdf")

# --- Extraction Functions ---
def extract_text_pdf(pdf_bytes):
    text = ""
    try:
        reader = PdfReader(io.BytesIO(pdf_bytes))
        text = "\n".join(page.extract_text() or "" for page in reader.pages)
    except Exception:
        pass
    return text

def extract_text_ocr(pdf_bytes):
    all_text = ""
    try:
        images = convert_from_bytes(pdf_bytes)
        for img in images:
            all_text += pytesseract.image_to_string(img) + "\n"
    except Exception:
        pass
    return all_text

def extract_rows(text):
    pattern = re.compile(
        r"Order\s*-\s*ID[:\s]*(?P<order>[^\n\r]+).*?"
        r"Item\s*No[:\s]*(?P<item>[^\n\r]+).*?"
        r"Supplier\s*product\s*code[:\s]*(?P<sup>[^\n\r]+).*?"
        r"Colour[:\s]*(?P<colour>[^\n\r]+).*?"
        r"6/9[:\s]*(?P<sixnine>[^\n\r]+).*?"
        r"9/12[:\s]*(?P<ninetwelve>[^\n\r]+).*?"
        r"12/18[:\s]*(?P<tweleigh>[^\n\r]+).*?"
        r"18/24[:\s]*(?P<eight24>[^\n\r]+).*?"
        r"24/36[:\s]*(?P<tfour36>[^\n\r]+)",
        re.IGNORECASE | re.DOTALL
    )
    rows = []
    for m in pattern.finditer(text):
        rows.append({
            "Order - ID": m.group("order").strip(),
            "Item No": m.group("item").strip(),
            "Supplier product code": m.group("sup").strip(),
            "Colour": m.group("colour").strip(),
            "6/9": m.group("sixnine").strip(),
            "9/12": m.group("ninetwelve").strip(),
            "12/18": m.group("tweleigh").strip(),
            "18/24": m.group("eight24").strip(),
            "24/36": m.group("tfour36").strip(),
        })
    return rows

# --- Main Processing ---
if uploaded:
    pdf_bytes = uploaded.read()
    text = extract_text_pdf(pdf_bytes)

    if not text.strip():
        st.warning("No text found — using OCR fallback.")
        text = extract_text_ocr(pdf_bytes)

    if not text.strip():
        st.error("No extractable text in PDF.")
        st.stop()

    rows = extract_rows(text)

    if rows:
        df_new = pd.DataFrame(rows)
        st.subheader("📋 Extracted Rows")
        st.dataframe(df_new)

        df_merged = pd.concat([df_excel, df_new], ignore_index=True)
        st.subheader("📦 Merged Data")
        st.dataframe(df_merged)

        csv_data = df_merged.to_csv(index=False).encode("utf-8")
        st.download_button("⬇️ Download Merged CSV", csv_data, "merged_data.csv", "text/csv")
    else:
        st.error("Could not parse any valid data rows from PDF.")

else:
    st.info("Please upload a PDF file.")

