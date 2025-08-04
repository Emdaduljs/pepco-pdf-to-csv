import streamlit as st
import gspread
from google.oauth2.service_account import Credentials

def get_gsheet_client():
    creds_dict = st.secrets["gcp_service_account"]
    scopes = [
        "https://www.googleapis.com/auth/spreadsheets",
        "https://www.googleapis.com/auth/drive.file",
    ]
    creds = Credentials.from_service_account_info(creds_dict, scopes=scopes)
    return gspread.authorize(creds)

def upload_to_gsheet(df, spreadsheet_url, sheet_name):
    client = get_gsheet_client()
    sheet = client.open_by_url(spreadsheet_url)

    if sheet_name:
        worksheet = sheet.add_worksheet(title=sheet_name, rows="100", cols="20")
    else:
        from datetime import datetime
        sheet_name = datetime.now().strftime("Export_%Y%m%d_%H%M%S")
        worksheet = sheet.add_worksheet(title=sheet_name, rows="100", cols="20")

    worksheet.update([df.columns.values.tolist()] + df.values.tolist())
    return spreadsheet_url
