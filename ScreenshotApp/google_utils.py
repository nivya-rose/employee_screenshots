import io
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseUpload
from google.oauth2.service_account import Credentials

SERVICE_ACCOUNT_FILE = 'ScreenshotApp/credentials.json'
SCOPES = [
    'https://www.googleapis.com/auth/drive.file',
    'https://www.googleapis.com/auth/spreadsheets'
]

creds = Credentials.from_service_account_file(SERVICE_ACCOUNT_FILE, scopes=SCOPES)
drive_service = build('drive', 'v3', credentials=creds)
sheets_service = build('sheets', 'v4', credentials=creds)

def upload_file_to_drive(file_obj, folder_id, new_name):
    file_metadata = {'name': new_name, 'parents': [folder_id]}
    media = MediaIoBaseUpload(file_obj, mimetype=file_obj.content_type)
    file = drive_service.files().create(body=file_metadata, media_body=media, fields='id').execute()
    return file.get('id')

def append_to_sheet(spreadsheet_id, values):
    body = {'values': [values]}
    sheets_service.spreadsheets().values().append(
        spreadsheetId=spreadsheet_id,
        range='Sheet1!A:D',
        valueInputOption='RAW',
        body=body
    ).execute()
