from googleapiclient.discovery import build
from google.oauth2.credentials import Credentials
from email.mime.text import MIMEText
import base64

def send_email(to_email,subject , message):
    creds= Credentials.from_authorized_user_file('token.json', ['https://www.googleapis.com/auth/gmail.send'])
    service = build('gmail', 'v1', credentials=creds)
    
    message = MIMEText(message)
    message['to'] = to_email
    message['subject'] = subject    
    raw = base64.urlsafe_b64encode(message.as_bytes()).decode()
    send_email=service.users().messages().send(userId='me', body={'raw': raw}).execute()
    
    return send_email