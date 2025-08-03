import streamlit as st
import pandas as pd
from converter import parse_pdf_to_dataframe  # Assumes this returns a list of DataFrames (tables)
from gsheet import upload_to_gsheet

st.set_page_config(page_title="PDF to Sheet", layout="centered")
st.title("📄 Upload PDF → Export to Google Sheet + CSV")

uploaded_pdf = st.file_uploader("📁 Upload your PDF", type="pdf")
spreadsheet_url = st.text_input("🔗 Google Spreadsheet URL (shareable link or ID)")
sheet_name = "Sheet1"  # Fixed to Sheet1 as per your latest request

if uploaded_pdf and spreadsheet_url:
    if st.button("🚀 Process & Export"):
        try:
            with st.spinner("⏳ Reading PDF..."):
                df_list = parse_pdf_to_dataframe(uploaded_pdf)  # should return list of tables (DataFrames)

            if not df_list or all(df.empty for df in df_list):
                st.error("❌ No valid tables found in PDF.")
            else:
                st.success(f"✅ Found {len(df_list)} table(s). Previewing first one:")
                st.dataframe(df_list[0])

                with st.spinner("📤 Uploading to Google Sheets..."):
                    gsheet_url = upload_to_gsheet(df_list, spreadsheet_url, sheet_name)

                st.success("✅ All tables uploaded to Google Sheet!")
                st.markdown(f"[🔗 Open Google Sheet]({gsheet_url})", unsafe_allow_html=True)

                combined_csv = pd.concat(df_list, ignore_index=True).to_csv(index=False).encode("utf-8")
                st.download_button("⬇ Download Combined CSV", data=combined_csv, file_name="converted.csv", mime="text/csv")

        except Exception as e:
            st.error("❌ An error occurred during processing.")
            st.exception(e)
else:
    st.info("📌 Upload a PDF and paste your Google Sheet URL to begin.")
