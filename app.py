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

# --- Helper: Extract multiple rows of fields from text ---
def extract_multiple_rows(text):
    # Pattern to match all occurrences of a block with all fields in sequence (you can adjust)
    # This example assumes fields appear together in a block in this order:
    # Order - ID, Item No, Supplier product code, Colour, 6/9, 9/12, 12/18, 18/24, 24/36
    # Each field is on its own line or separated by newline or spaces
    pattern = re.compile(
        r"Order\s*-\s*ID[:\s]*(?P<OrderID>[^\n\r]+)\s*"
        r"Item\s*No[:\s]*(?P<ItemNo>[^\n\r]+)\s*"
        r"Supplier\s*product\s*code[:\s]*(?P<SupplierProductCode>[^\n\r]+)\s*"
        r"Colour[:\s]*(?P<Colour>[^\n\r]+)\s*"
        r"6/9[:\s]*(?P<SixNine>[^\n\r]+)\s*"
        r"9/12[:\s]*(?P<NineTwelve>[^\n\r]+)\s*"
        r"12/18[:\s]*(?P<TwelveEighteen>[^\n\r]+)\s*"
        r"18/24[:\s]*(?P<EighteenTwentyFour>[^\n\r]+)\s*"
        r"24/36[:\s]*(?P<TwentyFourThirtySix>[^\n\r]+)",
        re.IGNORECASE
    )
    matches = pattern.finditer(text)
    rows = []
    for m in matches:
        rows.append({
            "Order - ID": m.group("OrderID").strip(),
            "Item No": m.group("ItemNo").strip(),
            "Supplier product code": m.group("SupplierProductCode").strip(),
            "Colour": m.group("Colour").strip(),
            "6/9": m.group("SixNine").strip(),
            "9/12": m.group("NineTwelve").strip(),
            "12/18": m.group("TwelveEighteen").strip(),
            "18/24": m.group("EighteenTwentyFour").strip(),
            "24/36": m.group("TwentyFourThirtySix").strip(),
        })
    return rows

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
        doc = fitz.open(temp_pdf_path)
        pdf_text = "\n".join([page.get_text() for page in doc])
        extracted_rows = extract_multiple_rows(pdf_text)
        if not extracted_rows:
            raise ValueError("No multiple rows found in text, trying OCR fallback...")
        method = "📝 Text Extraction (PyMuPDF)"
    except Exception:
        pdf_text = extract_ocr_text(temp_pdf_path)
        extracted_rows = extract_multiple_rows(pdf_text)
        if not extracted_rows:
            st.warning("No valid data found in PDF text or OCR.")
            extracted_rows = []
        method = "🧠 OCR Extraction (Tesseract)"

    # Show extracted rows
    if extracted_rows:
        extracted_df = pd.DataFrame(extracted_rows)
        st.subheader(f"🔍 Extracted Data Rows ({method})")
        st.dataframe(extracted_df, use_container_width=True)

        # Append extracted data rows to original Excel dataframe
        merged_df = pd.concat([df, extracted_df], ignore_index=True)
    else:
        merged_df = df
        st.info("No data rows extracted from PDF to append.")

    # Try extracting tables with pdfplumber
    try:
        table_data_csv = extract_table_data(temp_pdf_path)
        table_df = pd.read_csv(io.StringIO(table_data_csv)) if table_data_csv else None
        if table_df is not None:
            st.subheader("📄 Table Extracted from PDF (if any)")
            st.dataframe(table_df, use_container_width=True)
    except Exception as e:
        st.warning(f"Failed to extract table data: {e}")

    # Show final merged DataFrame
    st.subheader("📦 Final Merged Data")
    st.dataframe(merged_df, use_container_width=True)

    st.download_button("⬇️ Download Merged Data as CSV", merged_df.to_csv(index=False), "merged_data.csv", "text/csv")

else:
    st.info("Upload a PDF to extract and merge.")
