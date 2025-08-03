import gspread
from oauth2client.service_account import ServiceAccountCredentials

def get_gsheet_client():
    scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
    creds = ServiceAccountCredentials.from_json_keyfile_name("credentials.json", scope)
    return gspread.authorize(creds)

def upload_to_gsheet(df_list, spreadsheet_url, sheet_name):
    client = get_gsheet_client()
    if "docs.google.com" in spreadsheet_url:
        spreadsheet = client.open_by_url(spreadsheet_url)
    else:
        spreadsheet = client.open_by_key(spreadsheet_url)

    try:
        worksheet = spreadsheet.worksheet(sheet_name)
    except gspread.exceptions.WorksheetNotFound:
        worksheet = spreadsheet.add_worksheet(title=sheet_name, rows="1000", cols="26")

    worksheet.clear()

    start_row = 1
    for df in df_list:
        rows = [df.columns.tolist()] + df.values.tolist()
        end_row = start_row + len(rows) - 1
        cell_range = f"A{start_row}"
        worksheet.update(cell_range, rows)
        start_row = end_row + 1

    return spreadsheet.url
