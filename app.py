import streamlit as st

st.set_page_config(page_title="PDF to Sheet", layout="centered")
st.write("✅ App is running!")  # Debug: confirm app starts

# Debug block to verify imports
try:
    import pandas as pd
    import fitz  # PyMuPDF
    import gspread
    import googleapiclient.discovery
    st.write("All imports OK")
except Exception as e:
    st.error(f"Import error: {e}")
    st.stop()

from converter import parse_pdf_to_dataframe_bounding_boxes
from gsheet import upload_to_gsheet

st.title("📄 Upload PDF → Export to Google Sheet + CSV")

uploaded_pdf = st.file_uploader("📁 Upload your PDF", type="pdf")
spreadsheet_url = st.text_input("🔗 Google Spreadsheet URL")
sheet_name = st.text_input("📄 Sheet Name (optional)")  # Ignored by upload function

if uploaded_pdf and spreadsheet_url:
    if st.button("🚀 Process & Export"):
        try:
            with st.spinner("⏳ Reading PDF..."):
                df = parse_pdf_to_dataframe_bounding_boxes(uploaded_pdf)
            st.success("✅ PDF parsed")
            st.dataframe(df)
        except Exception as parse_err:
            st.error(f"Error parsing PDF: {parse_err}")
            st.stop()

        if not df.empty:
            try:
                with st.spinner("📤 Uploading to Google Sheets..."):
                    sheet_link = upload_to_gsheet(df, spreadsheet_url)
                st.success("✅ Exported to Google Sheets")
                st.markdown(f"[Open Google Sheet]({sheet_link})", unsafe_allow_html=True)

                csv_bytes = df.to_csv(index=False).encode("utf-8")
                st.download_button(
                    label="⬇ Download CSV",
                    data=csv_bytes,
                    file_name="converted.csv",
                    mime="text/csv"
                )
            except Exception as upload_err:
                st.error(f"Error uploading to Google Sheets: {upload_err}")
else:
    st.info("📌 Upload a PDF and paste your Google Sheet URL.")
