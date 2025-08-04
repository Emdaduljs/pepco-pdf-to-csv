import pandas as pd
import gspread
from google.oauth2.service_account import Credentials
from google.auth.transport.requests import Request
import streamlit as st

def upload_to_gsheet(dataframe):
    scopes = ["https://www.googleapis.com/auth/spreadsheets"]
    creds = Credentials.from_service_account_info(
        st.secrets["gcp_service_account"],
        scopes=scopes
    )
    gc = gspread.authorize(creds)

    # Open spreadsheet
    sh = gc.open_by_url(st.secrets["spreadsheet_url"])
    worksheet = sh.worksheet("Sheet3")

    # Clear existing data
    worksheet.clear()

    # Insert full data
    worksheet.update([dataframe.columns.tolist()] + dataframe.values.tolist())

    # Auto-format
    worksheet.format("A1:Z1", {"textFormat": {"bold": True}})
    worksheet.auto_resize_columns(1, len(dataframe.columns))
