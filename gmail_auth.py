# gmail_auth.py
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
import os

# Gmail send scope
SCOPES = ["https://www.googleapis.com/auth/gmail.send"]

def main():
    creds = None
    if os.path.exists("token.json"):
        creds = Credentials.from_authorized_user_file("token.json", SCOPES)

    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            # IMPORTANT: use credentials.json (downloaded from GCP), not token.json
            flow = InstalledAppFlow.from_client_secrets_file(
                "credentials.json", SCOPES
            )
            # Use a fixed port that is listed in your redirect URIs
            creds = flow.run_local_server(port=8080, access_type="offline", prompt="consent")

        with open("token.json", "w") as token:
            token.write(creds.to_json())

    print("✅ Gmail authentication successful — token.json created!")

if __name__ == "__main__":
    main()
