
import gspread
import pandas as pd
from google.oauth2.service_account import Credentials

def upload_to_gsheet(df, spreadsheet_url, sheet_name="Sheet3"):
    scope = [
        "https://www.googleapis.com/auth/spreadsheets",
        "https://www.googleapis.com/auth/drive"
    ]
    creds = Credentials.from_service_account_file("credentials.json", scopes=scope)
    client = gspread.authorize(creds)

    spreadsheet = client.open_by_url(spreadsheet_url)

    try:
        worksheet = spreadsheet.worksheet(sheet_name)
    except:
        worksheet = spreadsheet.add_worksheet(title=sheet_name, rows="100", cols="20")

    worksheet.clear()
    worksheet.update([df.columns.values.tolist()] + df.values.tolist())
