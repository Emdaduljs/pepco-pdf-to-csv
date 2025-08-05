import streamlit as st
import pandas as pd
from converter import parse_pdf_to_dataframe_bounding_boxes
from gsheet import upload_to_existing_sheet

st.set_page_config(page_title="PDF to Sheet", layout="centered")
st.title("📄 Upload PDF → Export to Google Sheet + CSV")

# File uploader
uploaded_pdf = st.file_uploader("📁 Upload your PDF", type="pdf")

# Dropdown to select Google Sheet
st.subheader("🔗 Select Google Sheet")
spreadsheet_option = st.selectbox("Choose a brand:", ["Pepco", "Pep&co"])

# Map option to URL
spreadsheet_url_map = {
    "Pepco": "https://docs.google.com/spreadsheets/d/1ug0VTy8iwUeSdpw4upHkVMxnwSekvYrxz6nm04_BJ-o/edit?usp=sharing",
    "Pep&co": "https://docs.google.com/spreadsheets/d/YOUR_OTHER_SHEET_ID/edit?usp=sharing"  # Replace with actual link
}
spreadsheet_url = spreadsheet_url_map.get(spreadsheet_option)

# Main logic
if uploaded_pdf and spreadsheet_url:
    if st.button("🚀 Process & Export"):
        try:
            with st.spinner("⏳ Reading PDF..."):
                df = parse_pdf_to_dataframe_bounding_boxes(uploaded_pdf)
            st.success("✅ PDF parsed successfully")
            st.dataframe(df)
        except Exception as e:
            st.error(f"❌ Error parsing PDF: {e}")
            st.stop()

        if not df.empty:
            if "ORDER" in df.columns and "ITEM" in df.columns:
                try:
                    with st.spinner("📤 Uploading to Google Sheets..."):
                        sheet_url = upload_to_existing_sheet(
                            df,
                            spreadsheet_url,
                            sheet_name="Sheet3",
                            auto_resize=True,
                            rename_with_timestamp=True
                        )
                    st.success("✅ Uploaded to Google Sheets")
                    st.markdown(f"[🔗 Open Sheet]({sheet_url})", unsafe_allow_html=True)

                    # Offer CSV download
                    csv = df.to_csv(index=False).encode("utf-8")
                    st.download_button("⬇ Download CSV", data=csv, file_name="converted.csv", mime="text/csv")
                except Exception as e:
                    st.error(f"❌ Error uploading to Google Sheets: {e}")
            else:
                st.error("❌ 'ORDER' and 'ITEM' columns not found in parsed data.")
else:
    st.info("📌 Please upload a PDF and select a brand to continue.")
