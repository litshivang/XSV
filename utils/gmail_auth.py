# gmail_auth.py
import os
import pickle
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request

SCOPES = ['https://www.googleapis.com/auth/gmail.modify']

def main():
    creds = None
    token_path = 'config/token.pickle'
    credentials_path = 'config/credentials.json'

    # Load existing token if available
    if os.path.exists(token_path):
        with open(token_path, 'rb') as token:
            creds = pickle.load(token)

    # If no valid credentials, generate new one
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(credentials_path, SCOPES)
            creds = flow.run_local_server(port=8080)  # Fixed port for stable redirect URI

        # Save token
        with open(token_path, 'wb') as token:
            pickle.dump(creds, token)

    print("✅ Gmail token saved to:", token_path)

if __name__ == '__main__':
    main()
