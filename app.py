import streamlit as st
import fitz  # PyMuPDF
import pandas as pd
from converter import extract_tables_from_pdf
from gsheet import upload_to_gsheet

st.set_page_config(page_title="PDF to Google Sheet - Pepco", layout="centered")

st.title("📄 PDF to Google Sheet - Pepco")
st.markdown("Upload a PDF file with tables. The app will extract data and upload to **Sheet3**.")

uploaded_file = st.file_uploader("Choose PDF file", type="pdf")

if uploaded_file:
    with open("temp.pdf", "wb") as f:
        f.write(uploaded_file.read())

    st.success("PDF uploaded. Extracting tables...")

    try:
        dfs = extract_tables_from_pdf("temp.pdf")
        if not dfs:
            st.error("No tables were detected in this PDF.")
        else:
            combined_df = pd.concat(dfs, ignore_index=True)
            st.write("✅ Table preview:", combined_df.head())

            # Upload full table to Google Sheets
            try:
                upload_to_gsheet(combined_df)
                st.success("✅ Uploaded to Google Sheets → Sheet3 successfully.")
            except Exception as e:
                st.error(f"❌ Error uploading to Google Sheets: {e}")

    except Exception as e:
        st.error(f"❌ Failed to extract data: {e}")
