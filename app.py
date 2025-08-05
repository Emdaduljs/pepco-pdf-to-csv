import streamlit as st
import pandas as pd
from converter import parse_pdf_to_dataframe
from gsheet import upload_to_gsheet

# CONFIG
st.set_page_config(page_title="Cuda Automation CSV Converter from PDF", layout="wide")
st.markdown(
    """
    <style>
        .left-panel {
            display: flex;
        }
        .logo {
            margin-right: 30px;
        }
        .main-panel {
            flex-grow: 1;
        }
    </style>
    """, unsafe_allow_html=True
)

# PASSWORD AUTH
st.sidebar.image("ui_logo.png", width=149)

st.sidebar.title("🔐 Login")
user_type = st.sidebar.selectbox("Login as", ["Editor", "User"])
password = st.sidebar.text_input("Enter password", type="password")

# PASSWORD VALIDATION
editor_password = "123"
user_password = "1234"

if (user_type == "Editor" and password != editor_password) or (user_type == "User" and password != user_password):
    st.warning("Please enter correct password to proceed.")
    st.stop()

# SPREADSHEET SELECTION
st.sidebar.title("📋 Select Spreadsheet")
spreadsheet_choice = st.sidebar.selectbox("Choose company", ["Pepco", "Pep&co"])

spreadsheet_urls = {
    "Pepco": "https://docs.google.com/spreadsheets/d/1ug0VTy8iwUeSdpw4upHkVMxnwSekvYrxz6nm04_BJ-o/edit?usp=sharing",
    "Pep&co": "https://docs.google.com/spreadsheets/d/your_other_spreadsheet_id_here"
}

spreadsheet_url = spreadsheet_urls[spreadsheet_choice]
spreadsheet_id = spreadsheet_url.split("/d/")[1].split("/")[0]

# DISPLAY APP UI
st.title("📄 Cuda Automation CSV Converter from PDF")

uploaded_pdf = st.file_uploader("📁 Upload your PDF", type="pdf")

if user_type == "Editor":
    if uploaded_pdf:
        df = parse_pdf_to_dataframe(uploaded_pdf)
        st.success("✅ PDF parsed successfully.")
        st.dataframe(df)

        if st.button("📤 Export to Google Sheet (Sheet3 only)"):
            try:
                upload_to_gsheet(df, spreadsheet_id, sheet_name="Sheet3")
                st.success("✅ Exported to Google Sheet (Sheet3).")
            except Exception as e:
                st.error(f"❌ Export failed: {e}")
else:
    st.info("🔒 You are logged in as User. You can only download data from Sheet1.")

# DOWNLOAD CSV FROM SHEET1 (Visible to both)
st.subheader("📥 Download from Sheet1")

try:
    sheet1_df = pd.read_csv(f"https://docs.google.com/spreadsheets/d/{spreadsheet_id}/gviz/tq?tqx=out:csv&sheet=Sheet1")
    st.dataframe(sheet1_df)
    st.download_button(
        label="⬇️ Download Sheet1 as CSV",
        data=sheet1_df.to_csv(index=False).encode("utf-8"),
        file_name="sheet1_export.csv",
        mime="text/csv"
    )
except Exception as e:
    st.error("❌ Failed to load Sheet1. Check spreadsheet permissions.")
