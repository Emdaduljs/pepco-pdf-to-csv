import gspread
from oauth2client.service_account import ServiceAccountCredentials
import pandas as pd
import datetime
import os
import json

def get_credentials():
    if "GCP_SERVICE_ACCOUNT" in os.environ:
        creds_dict = json.loads(os.environ["GCP_SERVICE_ACCOUNT"])
    else:
        with open("client_secret.json") as f:
            creds_dict = json.load(f)

    scope = [
        "https://spreadsheets.google.com/feeds",
        "https://www.googleapis.com/auth/drive"
    ]
    return ServiceAccountCredentials.from_json_keyfile_dict(creds_dict, scope)

def upload_to_gsheet(df: pd.DataFrame, spreadsheet_url: str, sheet_name: str = None):
    client = gspread.authorize(get_credentials())
    sheet = client.open_by_url(spreadsheet_url)

    if not sheet_name:
        sheet_name = "Export " + datetime.datetime.now().strftime("%Y-%m-%d %H:%M")

    worksheet = sheet.add_worksheet(title=sheet_name, rows=str(len(df)), cols=str(len(df.columns)))
    worksheet.update([df.columns.values.tolist()] + df.values.tolist())

    return spreadsheet_url
