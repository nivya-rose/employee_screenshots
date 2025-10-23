import io
from google.oauth2 import service_account
from googleapiclient.discovery import build
from django.conf import settings
from googleapiclient.http import MediaIoBaseUpload
from google.oauth2.service_account import Credentials

SCOPES = ['https://www.googleapis.com/auth/drive.readonly']
SERVICE_ACCOUNT_FILE = 'ScreenshotApp/credentials.json'


def get_drive_service():
    creds = service_account.Credentials.from_service_account_file(
        SERVICE_ACCOUNT_FILE, scopes=SCOPES)
    return build('drive', 'v3', credentials=creds)

def list_screenshots_from_folder(folder_id):
    service = get_drive_service()
    query = f"'{folder_id}' in parents and mimeType!='application/vnd.google-apps.folder' and trashed=false"
    results = service.files().list(
        q=query,
        fields="files(id, name, webViewLink)"
    ).execute()
    files = results.get('files', [])
    print("Files fetched from Drive:", files) 
    return files


SCOPES = ['https://www.googleapis.com/auth/drive.file']
SERVICE_ACCOUNT_FILE = 'ScreenshotApp/credentials.json'

creds = Credentials.from_service_account_file(SERVICE_ACCOUNT_FILE, scopes=SCOPES)
drive_service = build('drive', 'v3', credentials=creds)

def upload_file_to_drive(file_obj, folder_id):
    file_metadata = {'name': file_obj.name, 'parents': [folder_id]}
    media = MediaIoBaseUpload(file_obj, mimetype=file_obj.content_type)
    file = drive_service.files().create(body=file_metadata, media_body=media, fields='id').execute()
    return file.get('id')
