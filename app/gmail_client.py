import os
import pickle
import base64
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request

SCOPES = ['https://www.googleapis.com/auth/gmail.readonly']

CREDENTIALS_PATH = "credentials/credentials.json"
TOKEN_PATH = "token.pickle"


def authenticate_gmail():
    creds = None
    if os.path.exists(TOKEN_PATH):
        with open(TOKEN_PATH, 'rb') as token:
            creds = pickle.load(token)
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(CREDENTIALS_PATH, SCOPES)
            creds = flow.run_local_server(port=0)
        with open(TOKEN_PATH, 'wb') as token:
            pickle.dump(creds, token)
    return build('gmail', 'v1', credentials=creds)


def get_all_emails(service):
    """Récupère TOUTES les 549 emails"""
    max_results = 549
    emails = []
    fetched = 0
    next_page_token = None

    while True:
        results = service.users().messages().list(
            userId='me',
            labelIds=['INBOX'],
            maxResults=min(100, max_results - fetched),
            pageToken=next_page_token
        ).execute()

        messages = results.get('messages', [])
        for msg in messages:
            msg_data = service.users().messages().get(userId='me', id=msg['id']).execute()
            payload = msg_data['payload']
            headers = payload.get('headers', [])

            subject = next((h['value'] for h in headers if h['name'] == 'Subject'), 'Sans sujet')

            body = ''
            if 'parts' in payload:
                for part in payload['parts']:
                    if part.get('mimeType') == 'text/plain' and 'data' in part.get('body', {}):
                        body += base64.urlsafe_b64decode(part['body']['data']).decode(errors="ignore")
            else:
                if 'data' in payload.get('body', {}):
                    body = base64.urlsafe_b64decode(payload['body']['data']).decode(errors="ignore")

            emails.append({'subject': subject, 'body': body})
            fetched += 1

            if fetched >= max_results:
                return emails

        next_page_token = results.get('nextPageToken')
        if not next_page_token:
            break

    return emails
