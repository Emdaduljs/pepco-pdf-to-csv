import streamlit as st
import pandas as pd
from converter import parse_pdf_to_dataframe_bounding_boxes
from gsheet import upload_to_existing_sheet

# --- SETUP ---
st.set_page_config(page_title="PDF to Sheet", layout="centered")
st.title("📄 Upload PDF → Export to Google Sheet + CSV")

# --- Password Protection ---
st.sidebar.subheader("🔒 Login Required")
password = st.sidebar.text_input("Enter password", type="password")

if password not in ["123", "1234"]:
    st.warning("Please enter a valid password to continue.")
    st.stop()

role = "Editor" if password == "123" else "User"
st.sidebar.success(f"✅ Logged in as: {role}")

# --- File Upload ---
uploaded_pdf = st.file_uploader("📁 Upload your PDF", type="pdf")

# --- Google Sheet Selection ---
st.subheader("🔗 Select Google Sheet")
spreadsheet_option = st.selectbox("Choose a brand:", ["Pepco", "Pep&co"])

spreadsheet_url_map = {
    "Pepco": "https://docs.google.com/spreadsheets/d/1ug0VTy8iwUeSdpw4upHkVMxnwSekvYrxz6nm04_BJ-o/edit?usp=sharing",
    "Pep&co": "https://docs.google.com/spreadsheets/d/YOUR_OTHER_SHEET_ID/edit?usp=sharing"  # Replace this
}
spreadsheet_url = spreadsheet_url_map.get(spreadsheet_option)

# --- Main App Logic ---
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
                # Only editors can upload to Google Sheets
                if role == "Editor":
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
                    except Exception as e:
                        st.error(f"❌ Error uploading to Google Sheets: {e}")
                else:
                    st.info("🔒 Upload disabled for 'User' access.")

                # CSV Download allowed for all
                csv = df.to_csv(index=False).encode("utf-8")
                st.download_button("⬇ Download CSV", data=csv, file_name="converted.csv", mime="text/csv")
            else:
                st.error("❌ 'ORDER' and 'ITEM' columns not found in parsed data.")
else:
    st.info("📌 Please upload a PDF and select a brand to continue.")
