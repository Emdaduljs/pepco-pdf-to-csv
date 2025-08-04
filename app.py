import streamlit as st
import pandas as pd
import pdfplumber
import io
import datetime
from google.oauth2 import service_account
from googleapiclient.discovery import build

# ------------------- CONFIG -------------------
SHEET_NAME = 'Sheet3'
SCOPES = ["https://www.googleapis.com/auth/spreadsheets"]

# ------------------- LOAD GOOGLE SHEETS CLIENT -------------------
@st.cache_resource
def get_gsheet_client():
    credentials = service_account.Credentials.from_service_account_info(
        st.secrets["gcp_service_account"], scopes=SCOPES
    )
    return build("sheets", "v4", credentials=credentials)

# ------------------- PARSE PDF -------------------
def extract_tables_from_pdf(uploaded_pdf):
    pdf_data = []
    with pdfplumber.open(uploaded_pdf) as pdf:
        for page in pdf.pages:
            tables = page.extract_tables()
            for table in tables:
                df = pd.DataFrame(table)
                df = df.dropna(how="all")  # Drop fully empty rows
                if not df.empty:
                    pdf_data.append(df)
    return pd.concat(pdf_data, ignore_index=True) if pdf_data else pd.DataFrame()

# ------------------- EXPORT TO GOOGLE SHEETS -------------------
def export_to_sheet(df, sheet_id):
    service = get_gsheet_client()
    sheet = service.spreadsheets()

    # Clear Sheet3
    sheet.values().clear(
        spreadsheetId=sheet_id,
        range=SHEET_NAME
    ).execute()

    # Upload new data
    values = df.astype(str).values.tolist()
    sheet.values().update(
        spreadsheetId=sheet_id,
        range=SHEET_NAME,
        valueInputOption="RAW",
        body={"values": [df.columns.tolist()] + values}
    ).execute()

# ------------------- STREAMLIT UI -------------------
st.title("📄 PDF to Google Sheet - Pepco")

sheet_id = st.secrets["spreadsheet_id"]
uploaded_pdf = st.file_uploader("Upload PDF", type=["pdf"])

if uploaded_pdf:
    try:
        st.info("Parsing PDF...")
        df = extract_tables_from_pdf(uploaded_pdf)

        if df.empty:
            st.error("No table found in PDF.")
        else:
            st.dataframe(df, use_container_width=True)
            st.success("✅ Table extracted.")

            export_to_sheet(df, sheet_id)
            st.success(f"✅ Data exported to '{SHEET_NAME}' in your Google Sheet.")
    except Exception as e:
        st.error(f"❌ Error: {e}")
