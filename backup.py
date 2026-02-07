import gspread
from oauth2client.service_account import ServiceAccountCredentials
from sheets import connect_sheet

SCOPE = [
    "https://spreadsheets.google.com/feeds",
    "https://www.googleapis.com/auth/drive"
]

def connect_sheet():
    creds = ServiceAccountCredentials.from_json_keyfile_name(
        "credentials.json", SCOPE
    )
    client = gspread.authorize(creds)
    sheet = client.open("Free4U_Backup").sheet1
    return sheet

def backup_to_sheet(files_data):
    sheet = connect_sheet()
    sheet.clear()
    sheet.append_row(
        ["name", "description", "note", "image", "download"]
    )
    for name, data in files_data.items():
        sheet.append_row([
            name,
            data["description"],
            data["note"],
            data["image"],
            data["download"]
        ])
