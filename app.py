import streamlit as st
import pandas as pd
from converter import parse_pdf_to_dataframe_bounding_boxes
from gsheet import upload_to_existing_sheet, download_sheet_as_df
from PIL import Image

# --- SETUP ---
st.set_page_config(page_title="Cuda Automation CSV Converter", layout="centered")
st.title("📄 Cuda Automation CSV Converter from PDF")

# --- SIDEBAR LOGIN & LOGO ---
st.sidebar.subheader("🔒 Login Required")

# Predefined login credentials
users = {
    "Emdaduljs": "123",     # Editor
    "Test1": "1234",        # User
    "Test2": "12345",       # User
    "Test3": "123456",      # User
}

username = st.sidebar.selectbox("Username", list(users.keys()))
password = st.sidebar.text_input("Password", type="password")

# Load logo image
try:
    logo = Image.open("ui_logo.png")
    st.sidebar.image(logo, width=149)
except Exception:
    st.sidebar.warning("⚠️ Logo not found (ui_logo.png)")

# Validate login
if password != users.get(username):
    st.warning("❌ Invalid username or password.")
    st.stop()

# Assign role
role = "Editor" if username == "Emdaduljs" else "User"
st.sidebar.success(f"✅ Logged in as: {role} ({username})")

# --- BRAND SHEET SELECTION ---
st.subheader("🔗 Select Your Automation's Buyer")
spreadsheet_option = st.selectbox("Choose a brand:", ["Pepco", "Pep&co"])

spreadsheet_url_map = {
    "Pepco": "https://docs.google.com/spreadsheets/d/1ug0VTy8iwUeSdpw4upHkVMxnwSekvYrxz6nm04_BJ-o/edit?usp=sharing",
    "Pep&co": "https://docs.google.com/spreadsheets/d/YOUR_OTHER_SHEET_ID/edit?usp=sharing"
}
spreadsheet_url = spreadsheet_url_map.get(spreadsheet_option)

# --- UPLOAD PDF AND PROCESS ---
if role == "Editor":
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

            try:
                with st.spinner("📤 Uploading to Google Sheets (Sheet3)..."):
                    sheet_url = upload_to_existing_sheet(
                        df,
                        spreadsheet_url,
                        sheet_name="Sheet3",
                        auto_resize=True,
                        rename_with_timestamp=False
                    )
                st.success("✅ Uploaded to Google Sheets")
                st.markdown(f"[🔗 Open Sheet]({sheet_url})", unsafe_allow_html=True)
            except Exception as e:
                st.error(f"❌ Error uploading to Google Sheets: {e}")

            csv = df.to_csv(index=False).encode("utf-8")
            st.download_button("⬇ Download CSV (Parsed PDF)", data=csv, file_name="converted.csv", mime="text/csv")
    else:
        st.info("📌 Please upload a PDF to continue.")

# --- USER & EDITOR: DOWNLOAD FROM SHEET1 ---
st.markdown("---")
st.info("🔽 Download CSV from Sheet1")

# Optional search filter
search_term = st.text_input("🔍 Enter word to filter rows in Sheet1 (leave empty for all rows):")

if st.button("⬇ Download CSV from Sheet1"):
    try:
        df_sheet1 = download_sheet_as_df(spreadsheet_url, sheet_name="Sheet1")

        if search_term:
            search_term_lower = search_term.lower()
            # Check if search term in headers
            header_match = any(search_term_lower in str(col).lower() for col in df_sheet1.columns)

            if header_match:
                filtered_df = df_sheet1
            else:
                # Filter rows where any cell contains search term
                mask = df_sheet1.apply(lambda row: row.astype(str).str.lower().str.contains(search_term_lower).any(), axis=1)
                filtered_df = df_sheet1[mask]
        else:
            filtered_df = df_sheet1

        if filtered_df.empty:
            st.warning("⚠️ No matching rows found for the search term.")
        else:
            csv = filtered_df.to_csv(index=False).encode("utf-8")
            st.download_button("⬇ Download Filtered CSV (Sheet1)", data=csv, file_name="sheet1_filtered_data.csv", mime="text/csv")

    except Exception as e:
        st.error(f"❌ Failed to download Sheet1 data: {e}")
