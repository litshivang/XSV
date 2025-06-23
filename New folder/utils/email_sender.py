# email_sender.py
import os
import base64
import pickle
from email.message import EmailMessage
from google.auth.transport.requests import Request
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build

SCOPES = ['https://www.googleapis.com/auth/gmail.send']

class GmailEmailSender:
    def __init__(self):
        self.service = self.authenticate()

    def authenticate(self):
        creds = None
        token_path = 'config/token.pickle'
        credentials_path = 'config/credentials.json'

        if os.path.exists(token_path):
            with open(token_path, 'rb') as token:
                creds = pickle.load(token)

        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                flow = InstalledAppFlow.from_client_secrets_file(credentials_path, SCOPES)
                creds = flow.run_local_server(port=0)
                with open(token_path, 'wb') as token:
                    pickle.dump(creds, token)

        return build('gmail', 'v1', credentials=creds)

    def send_email_with_attachment(self, to_email: str, subject: str, body_text: str, attachment_path: str) -> bool:
        try:
            message = EmailMessage()
            message.set_content(body_text)
            message['To'] = to_email
            message['From'] = 'me'
            message['Subject'] = subject

            with open(attachment_path, 'rb') as f:
                file_data = f.read()
                file_name = os.path.basename(attachment_path)

            message.add_attachment(file_data, maintype='application', subtype='octet-stream', filename=file_name)

            encoded_message = base64.urlsafe_b64encode(message.as_bytes()).decode()
            create_message = {'raw': encoded_message}

            self.service.users().messages().send(userId='me', body=create_message).execute()
            print(f"✅ Sent email to {to_email}")
            return True

        except Exception as e:
            print(f"❌ Error sending email: {e}")
            return False
