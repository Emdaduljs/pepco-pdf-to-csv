import streamlit as st
from google.oauth2.service_account import Credentials
from googleapiclient.discovery import build
import pandas as pd

def get_sheets_service():
    creds_dict = st.secrets["gcp_service_account"]
    scopes = ["https://www.googleapis.com/auth/spreadsheets"]
    creds = Credentials.from_service_account_info(creds_dict, scopes=scopes)
    return build("sheets", "v4", credentials=creds)

def upload_to_existing_sheet(df, spreadsheet_url, sheet_name="Sheet3", auto_resize=True, rename_with_timestamp=False):
    # Force write only to "Sheet3"
    sheet_name = "Sheet3"
    rename_with_timestamp = False  # Disable renaming completely

    sheet_id = spreadsheet_url.split("/d/")[1].split("/")[0]
    service = get_sheets_service()

    # Get sheet ID for the named sheet
    spreadsheet = service.spreadsheets().get(spreadsheetId=sheet_id).execute()
    sheets = spreadsheet["sheets"]
    sheet_id_num = None
    for s in sheets:
        if s["properties"]["title"] == sheet_name:
            sheet_id_num = s["properties"]["sheetId"]
            break
    if sheet_id_num is None:
        raise Exception(f"Sheet '{sheet_name}' not found in spreadsheet.")

    # Clear old data
    service.spreadsheets().values().clear(
        spreadsheetId=sheet_id,
        range=f"{sheet_name}!A:Z"
    ).execute()

    # Upload new data
    body = {
        "values": [df.columns.tolist()] + df.values.tolist()
    }
    service.spreadsheets().values().update(
        spreadsheetId=sheet_id,
        range=f"{sheet_name}!A1",
        valueInputOption="RAW",
        body=body
    ).execute()

    # Auto-resize columns
    if auto_resize:
        service.spreadsheets().batchUpdate(
            spreadsheetId=sheet_id,
            body={
                "requests": [{
                    "autoResizeDimensions": {
                        "dimensions": {
                            "sheetId": sheet_id_num,
                            "dimension": "COLUMNS",
                            "startIndex": 0,
                            "endIndex": len(df.columns)
                        }
                    }
                }]
            }
        ).execute()

    return spreadsheet_url

def download_sheet_as_df(spreadsheet_url, sheet_name="Sheet1"):
    sheet_id = spreadsheet_url.split("/d/")[1].split("/")[0]
    service = get_sheets_service()

    result = service.spreadsheets().values().get(
        spreadsheetId=sheet_id,
        range=sheet_name
    ).execute()

    values = result.get("values", [])
    if not values:
        raise Exception(f"No data found in sheet '{sheet_name}'.")

    columns = values[0]
    data = values[1:]

    df = pd.DataFrame(data, columns=columns)

    for col in df.columns:
        df[col] = pd.to_numeric(df[col], errors='ignore')

    return df
