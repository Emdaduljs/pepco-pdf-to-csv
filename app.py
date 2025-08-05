import streamlit as st
import pandas as pd
from converter import parse_pdf_to_dataframe_bounding_boxes
from gsheet import upload_to_existing_sheet, download_sheet_as_df  # Assume this function is implemented
from PIL import Image

# --- SETUP ---
st.set_page_config(page_title="Cuda Automation CSV Converter", layout="centered")
st.title("📄 Cuda Automation CSV Converter from PDF")

# --- SIDEBAR LOGIN & LOGO ---
st.sidebar.subheader("🔒 Login Required")
password = st.sidebar.text_input("Enter password", type="password")

# Logo below password
try:
    logo = Image.open("ui_logo.png")
    st.sidebar.image(logo, width=149)
except Exception:
    st.sidebar.warning("⚠️ Logo not found (ui_logo.png)")

# Password check
if password not in ["123", "1234"]:
    st.warning("Please enter a valid password to continue.")
    st.stop()

role = "Editor" if password == "123" else "User"
st.sidebar.success(f"✅ Logged in as: {role}")

# --- BRAND SHEET SELECTION ---
st.subheader("🔗 Select Your Automation's Buyer")
spreadsheet_option = st.selectbox("Choose a brand:", ["Pepco", "Pep&co"])

spreadsheet_url_map = {
    "Pepco": "https://docs.google.com/spreadsheets/d/1ug0VTy8iwUeSdpw4upHkVMxnwSekvYrxz6nm04_BJ-o/edit?usp=sharing",
    "Pep&co": "https://docs.google.com/spreadsheets/d/YOUR_OTHER_SHEET_ID/edit?usp=sharing"  # Replace with actual
}
spreadsheet_url = spreadsheet_url_map.get(spreadsheet_option)

# --- MAIN LOGIC ---

if role == "Editor":
    # Editor can upload
    uploaded_pdf = st.file_uploader("📁 Upload your PDF", type="pdf")
    if uploaded_pdf:
        if st.button("🚀 Convert and Export"):
            try:
                with st.spinner("⏳ Reading and parsing PDF..."):
                    df = parse_pdf_to_dataframe_bounding_boxes(uploaded_pdf)
                st.success("✅ PDF parsed successfully")
                st.dataframe(df)
            except Exception as e:
                st.error(f"❌ Error parsing PDF: {e}")
                st.stop()

            # Upload to Google Sheets Sheet3
            try:
                with st.spinner("📤 Uploading to Google Sheets (Sheet3)..."):
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

            # CSV download of parsed data (Editor)
            csv = df.to_csv(index=False).encode("utf-8")
            st.download_button("⬇ Download CSV (Parsed PDF)", data=csv, file_name="converted.csv", mime="text/csv")

    else:
        st.info("📌 Please upload a PDF to continue.")

else:
    # User role: no upload, only download CSV from Sheet1
    st.info("🔒 You are logged in as User. Upload disabled. You can download CSV from Sheet1.")

    if st.button("⬇ Download CSV from Sheet1"):
        try:
            # fetch sheet1 dataframe live from spreadsheet_url
            df_sheet1 = download_sheet_as_df(spreadsheet_url, sheet_name="Sheet1")
            csv = df_sheet1.to_csv(index=False).encode("utf-8")
            st.download_button("⬇ Download CSV", data=csv, file_name="sheet1_data.csv", mime="text/csv")
        except Exception as e:
            st.error(f"❌ Failed to download Sheet1 data: {e}")
