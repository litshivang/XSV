# email_fetcher.py
import base64
import email
import os.path
import pickle
from typing import List, Dict
from googleapiclient.discovery import build
from google.auth.transport.requests import Request
from google_auth_oauthlib.flow import InstalledAppFlow

SCOPES = ["https://www.googleapis.com/auth/gmail.modify"]


def fetch_live_emails(max_results=10) -> List[Dict]:
    creds = None
    token_path = "config/token.pickle"
    credentials_path = "config/credentials.json"

    if os.path.exists(token_path):
        with open(token_path, "rb") as token:
            creds = pickle.load(token)

    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(credentials_path, SCOPES)
            creds = flow.run_local_server(port=8080)
            with open(token_path, "wb") as token:
                pickle.dump(creds, token)

    service = build("gmail", "v1", credentials=creds)
    results = (
        service.users()
        .messages()
        .list(
            userId="me",
            labelIds=["INBOX"],
            q="is:unread from:shivangnvyas@gmail.com",
            maxResults=max_results,
        )
        .execute()
    )

    messages = results.get("messages", [])
    emails = []

    for msg in messages:
        msg_id = msg["id"]
        msg_data = (
            service.users()
            .messages()
            .get(userId="me", id=msg_id, format="full")
            .execute()
        )
        payload = msg_data.get("payload", {})
        headers = payload.get("headers", [])

        subject = next((h["value"] for h in headers if h["name"] == "Subject"), "")
        sender = next((h["value"] for h in headers if h["name"] == "From"), "")

        parts = payload.get("parts", [])
        body = ""

        for part in parts:
            if part.get("mimeType") == "text/plain":
                data = part["body"].get("data")
                if data:
                    body = base64.urlsafe_b64decode(data).decode()
                    break

        emails.append({"sender": sender, "subject": subject, "body": body})

        # ✅ Mark as read
        service.users().messages().modify(
            userId="me", id=msg_id, body={"removeLabelIds": ["UNREAD"]}
        ).execute()

    return emails
