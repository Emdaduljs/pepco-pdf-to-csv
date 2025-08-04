import gspread
from google.oauth2.service_account import Credentials
from datetime import datetime
import googleapiclient.discovery

def get_gsheet_client():
    creds_dict = st.secrets["gcp_service_account"]
    scopes = [
        "https://www.googleapis.com/auth/spreadsheets",
        "https://www.googleapis.com/auth/drive.file"
    ]
    creds = Credentials.from_service_account_info(creds_dict, scopes=scopes)
    return gspread.authorize(creds)

def upload_to_gsheet(df, spreadsheet_url):
    client = get_gsheet_client()
    sheet = client.open_by_url(spreadsheet_url)

    # Delete "Sheet3" if it exists
    try:
        old_ws = sheet.worksheet("Sheet3")
        sheet.del_worksheet(old_ws)
    except gspread.exceptions.WorksheetNotFound:
        pass

    # Timestamped worksheet name
    sheet_name = datetime.now().strftime("Export_%Y%m%d_%H%M")
    worksheet = sheet.add_worksheet(title=sheet_name, rows=str(len(df)+5), cols=str(len(df.columns)+5))

    # Upload data
    worksheet.update([df.columns.values.tolist()] + df.values.tolist())

    # Auto resize & format
    resize_columns(sheet.id, worksheet._properties["sheetId"], len(df.columns))
    format_header(sheet.id, worksheet._properties["sheetId"], len(df.columns))

    return f"{spreadsheet_url}#gid={worksheet.id}"

def resize_columns(spreadsheet_id, sheet_id, num_cols):
    creds_dict = st.secrets["gcp_service_account"]
    scopes = ["https://www.googleapis.com/auth/spreadsheets"]
    creds = Credentials.from_service_account_info(creds_dict, scopes=scopes)

    service = googleapiclient.discovery.build("sheets", "v4", credentials=creds)
    requests = [{
        "autoResizeDimensions": {
            "dimensions": {
                "sheetId": sheet_id,
                "dimension": "COLUMNS",
                "startIndex": 0,
                "endIndex": num_cols
            }
        }
    }]
    body = {"requests": requests}
    service.spreadsheets().batchUpdate(spreadsheetId=spreadsheet_id, body=body).execute()

def format_header(spreadsheet_id, sheet_id, num_cols):
    creds_dict = st.secrets["gcp_service_account"]
    scopes = ["https://www.googleapis.com/auth/spreadsheets"]
    creds = Credentials.from_service_account_info(creds_dict, scopes=scopes)

    service = googleapiclient.discovery.build("sheets", "v4", credentials=creds)
    requests = [{
        "repeatCell": {
            "range": {
                "sheetId": sheet_id,
                "startRowIndex": 0,
                "endRowIndex": 1,
                "startColumnIndex": 0,
                "endColumnIndex": num_cols
            },
            "cell": {
                "userEnteredFormat": {
                    "textFormat": {"bold": True}
                }
            },
            "fields": "userEnteredFormat.textFormat.bold"
        }
    }]
    body = {"requests": requests}
    service.spreadsheets().batchUpdate(spreadsheetId=spreadsheet_id, body=body).execute()
