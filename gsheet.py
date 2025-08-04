import gspread
from google.oauth2.service_account import Credentials
from datetime import datetime
import pandas as pd
import streamlit as st

SCOPES = ["https://www.googleapis.com/auth/spreadsheets"]
HEADERS = ['ORDER', 'ITEM']

def upload_to_gsheet(df, spreadsheet_url):
    df.columns = df.columns.str.upper().str.strip()
    df = df[[col for col in df.columns if col in HEADERS]]

    # Ensure both headers are present
    for col in HEADERS:
        if col not in df.columns:
            df[col] = ""

    df = df[HEADERS]

    # Final formatted output
    output_data = [HEADERS] + df.values.tolist()

    creds = Credentials.from_service_account_info(
        st.secrets["gcp_service_account"],
        scopes=SCOPES
    )
    client = gspread.authorize(creds)
    spreadsheet = client.open_by_url(spreadsheet_url)

    # Remove old Sheet3 if it exists
    try:
        spreadsheet.del_worksheet(spreadsheet.worksheet("Sheet3"))
    except:
        pass

    # Add new sheet with timestamp
    timestamp = datetime.now().strftime("Sheet3_%Y%m%d_%H%M%S")
    worksheet = spreadsheet.add_worksheet(title=timestamp, rows="1000", cols="20")
    worksheet.update("A1", output_data)

    # Bold headers
    worksheet.format("A1:Z1", {"textFormat": {"bold": True}})

    # Resize columns
    for i in range(len(HEADERS)):
        worksheet.set_column_width(i, 160)

    return f"https://docs.google.com/spreadsheets/d/{spreadsheet.id}/edit#gid={worksheet.id}"
