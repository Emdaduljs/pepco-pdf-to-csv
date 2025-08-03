import streamlit as st
import pandas as pd
from converter import parse_pdf_to_dataframe
from gsheet import upload_to_gsheet

st.set_page_config(page_title="PDF to Sheet", layout="centered")
st.title("📄 Upload PDF → Export to Google Sheet + CSV")

uploaded_pdf = st.file_uploader("📁 Upload your PDF", type="pdf")
spreadsheet_url = st.text_input("🔗 Google Spreadsheet URL")
sheet_name = st.text_input("📄 Sheet Name (optional)")

if uploaded_pdf and spreadsheet_url:
    if st.button("🚀 Process & Export"):
        with st.spinner("⏳ Reading PDF..."):
            df = parse_pdf_to_dataframe(uploaded_pdf)
        st.success("✅ PDF parsed")
        st.dataframe(df)

        if not df.empty:
            with st.spinner("📤 Uploading to Google Sheets..."):
                gsheet_url = upload_to_gsheet(df, spreadsheet_url, sheet_name)
            st.success("✅ Uploaded to Google Sheets")
            st.markdown(f"[Open Google Sheet]({gsheet_url})", unsafe_allow_html=True)

            csv = df.to_csv(index=False).encode("utf-8")
            st.download_button("⬇ Download CSV", data=csv, file_name="converted.csv", mime="text/csv")
else:
    st.info("📌 Upload a PDF and paste your Google Sheet URL.")
