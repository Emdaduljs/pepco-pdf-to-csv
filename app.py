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

# --- UPLOAD MULTIPLE PDFs AND PROCESS ---
st.markdown("### 📁 Upload up to 6 PDFs to convert and export")
uploaded_pdfs = st.file_uploader("Upload PDF files", type="pdf", accept_multiple_files=True)

sheet_targets = ["Sheet3", "Sheet4", "Sheet5", "Sheet6", "Sheet7", "Sheet8"]
user_uploaded = False  # Track if user has exported PDFs

if uploaded_pdfs:
    if len(uploaded_pdfs) > 6:
        st.warning("⚠️ You can upload a maximum of 6 PDFs only.")
    elif st.button("🚀 Convert and Export All"):
        for i, pdf_file in enumerate(uploaded_pdfs):
            sheet_name = sheet_targets[i]
            if role == "Editor":
                st.markdown(f"#### 📄 Processing File {i+1} → `{sheet_name}`")
            try:
                with st.spinner(f"⏳ Parsing PDF {i+1}..."):
                    df = parse_pdf_to_dataframe_bounding_boxes(pdf_file)
                if role == "Editor":
                    st.success(f"✅ PDF {i+1} parsed successfully")
                    st.dataframe(df)
            except Exception as e:
                st.error(f"❌ Error parsing PDF {i+1}: {e}")
                continue

            try:
                with st.spinner(f"📤 Uploading to {sheet_name}..."):
                    sheet_url = upload_to_existing_sheet(
                        df,
                        spreadsheet_url,
                        sheet_name=sheet_name,
                        auto_resize=True,
                        rename_with_timestamp=False
                    )
                if role == "Editor":
                    st.success(f"✅ Uploaded to Google Sheets → `{sheet_name}`")
                    st.markdown(f"[🔗 Open Sheet: {sheet_name}]({sheet_url})", unsafe_allow_html=True)
            except Exception as e:
                st.error(f"❌ Error uploading to {sheet_name}: {e}")
                continue

            if role == "Editor":
                csv_data = df.to_csv(index=False).encode("utf-8")
                st.download_button(
                    f"⬇ Download CSV for {sheet_name}",
                    data=csv_data,
                    file_name=f"{sheet_name.lower()}_converted.csv",
                    mime="text/csv"
                )
            else:
                user_uploaded = True  # Mark for download section

# --- USER: Post-upload download of Sheet1 & Label_Name ---
if role == "User" and user_uploaded:
    st.markdown("---")
    st.info("📥 Download Converted Data")
    if st.button("⬇ Download All CSV (Sheet1 + Label_Name)"):
        try:
            df1 = download_sheet_as_df(spreadsheet_url, sheet_name="Sheet1")
            df2 = download_sheet_as_df(spreadsheet_url, sheet_name="Label_Name")

            csv1 = df1.to_csv(index=False).encode("utf-8")
            csv2 = df2.to_csv(index=False).encode("utf-8")

            st.download_button("⬇ Download Sheet1 CSV", data=csv1, file_name="Sheet1.csv", mime="text/csv")
            st.download_button("⬇ Download Label_Name CSV", data=csv2, file_name="Label_Name.csv", mime="text/csv")
        except Exception as e:
            st.error(f"❌ Error downloading files: {e}")

# --- EDITOR: Download Filtered Sheet1 CSV ---
if role == "Editor":
    st.markdown("---")
    st.info("🔽 Download CSV from Sheet1")

    search_term = st.text_input("🔍 Enter word to filter rows in Sheet1 (leave empty for all rows):")

    if st.button("⬇ Download CSV from Sheet1"):
        try:
            df_sheet1 = download_sheet_as_df(spreadsheet_url, sheet_name="Sheet1")

            if search_term:
                search_term_lower = search_term.lower()
                header_match = any(search_term_lower in str(col).lower() for col in df_sheet1.columns)
                cell_match = df_sheet1.apply(lambda row: row.astype(str).str.lower().str.contains(search_term_lower).any(), axis=1).any()

                if header_match or cell_match:
                    filtered_df = df_sheet1
                else:
                    filtered_df = pd.DataFrame()
            else:
                filtered_df = df_sheet1

            if filtered_df.empty:
                st.warning("⚠️ No matching rows found for the search term.")
            else:
                csv = filtered_df.to_csv(index=False).encode("utf-8")
                st.download_button("⬇ Download Filtered CSV (Sheet1)", data=csv, file_name="sheet1_filtered_data.csv", mime="text/csv")

        except Exception as e:
            st.error(f"❌ Failed to download Sheet1 data: {e}")
