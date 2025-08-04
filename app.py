import streamlit as st
import tempfile
import os

from converter import extract_tables_from_pdf
from gsheet import upload_to_gsheet

st.title("PDF to Google Sheets - Pepco")

spreadsheet_url = st.secrets["spreadsheet_url"]

uploaded_file = st.file_uploader("Upload your PDF", type=["pdf"])

if uploaded_file:
    with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp:
        tmp.write(uploaded_file.read())
        pdf_path = tmp.name

    st.info("Processing PDF...")
    df = extract_tables_from_pdf(pdf_path)

    if df.empty:
        st.error("No valid tables found in PDF.")
    else:
        st.success("Tables extracted. Uploading to Google Sheets...")
        try:
            sheet_link = upload_to_gsheet(df, spreadsheet_url)
            st.success("Upload successful!")
            st.markdown(f"[Open Sheet]({sheet_link})")
        except Exception as e:
            st.error(f"Error uploading to Google Sheets: {e}")

    os.remove(pdf_path)
