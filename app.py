import streamlit as st
import pdfplumber
import pandas as pd
from datetime import datetime
from google.oauth2 import service_account
from googleapiclient.discovery import build

# Setup
st.set_page_config(page_title="PDF to Sheet", layout="wide")
st.title("📄 PDF to Google Sheet - Pepco")

# Auth
creds = service_account.Credentials.from_service_account_info(
    st.secrets["gcp_service_account"],
    scopes=["https://www.googleapis.com/auth/spreadsheets"]
)
sheet_id = st.secrets["spreadsheet_url"].split("/d/")[1].split("/")[0]
service = build("sheets", "v4", credentials=creds)
sheet = service.spreadsheets()

# PDF upload
uploaded_file = st.file_uploader("Upload PDF", type="pdf")
if uploaded_file:
    with pdfplumber.open(uploaded_file) as pdf:
        all_tables = []
        for page in pdf.pages:
            tables = page.extract_tables()
            for table in tables:
                df = pd.DataFrame(table)
                all_tables.append(df)

    if not all_tables:
        st.warning("No tables found in PDF.")
        st.stop()

    # Merge and clean
    df_all = pd.concat(all_tables, ignore_index=True).dropna(how="all")
    
    # Find headers
    headers = df_all.iloc[0].tolist()
    if "ORDER" in headers and "ITEM" in headers:
        df_final = df_all[1:]  # Skip header row
        df_final.columns = headers
        df_final.reset_index(drop=True, inplace=True)
    else:
        st.error("Required headers 'ORDER' and 'ITEM' not found.")
        st.write("Detected headers:", headers)
        st.stop()

    st.subheader("Extracted Table")
    st.dataframe(df_final)

    # Upload to Google Sheets
    sheet_name = "Sheet3"
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    try:
        # Clear old data
        sheet.values().clear(spreadsheetId=sheet_id, range=f"{sheet_name}!A:Z").execute()

        # Insert header
        values = [list(df_final.columns)] + df_final.values.tolist()
        body = {"values": values}
        sheet.values().update(
            spreadsheetId=sheet_id,
            range=f"{sheet_name}!A1",
            valueInputOption="RAW",
            body=body
        ).execute()

        # Resize columns
        sheet.batchUpdate(
            spreadsheetId=sheet_id,
            body={
                "requests": [{
                    "autoResizeDimensions": {
                        "dimensions": {
                            "sheetId": 2,  # Sheet3 is index 2 (adjust if different)
                            "dimension": "COLUMNS",
                            "startIndex": 0,
                            "endIndex": len(df_final.columns)
                        }
                    }
                }]
            }
        ).execute()

        # Optional: Rename sheet
        # sheet.batchUpdate(
        #     spreadsheetId=sheet_id,
        #     body={
        #         "requests": [{
        #             "updateSheetProperties": {
        #                 "properties": {
        #                     "sheetId": 2,
        #                     "title": f"Sheet_{timestamp}"
        #                 },
        #                 "fields": "title"
        #             }
        #         }]
        #     }
        # ).execute()

        st.success("✅ Data uploaded to Google Sheets: Sheet3")

    except Exception as e:
        st.error(f"❌ Error uploading to Google Sheets: {e}")
