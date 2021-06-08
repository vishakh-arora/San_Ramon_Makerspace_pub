from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
import os
import config

class Spreadsheet:
    # reading google sheets data
    # FOR MAKERSPACE UPDATE SPREADSHEET_ID AND CREDENTIALS FILE ONLY
    def __init__(self, spreadsheet_id):
        # API protocol
        creds = None
        self.spreadsheet_id = spreadsheet_id
        if os.path.exists('token.json'):
          creds = Credentials.from_authorized_user_file('token.json', config.SCOPES)

        if not creds or not creds.valid:
          if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
          else:
            flow = InstalledAppFlow.from_client_secrets_file('credentials.json', config.SCOPES)
            creds = flow.run_local_server(port=0)
          # Save the credentials for the next run
          with open('token.json', 'w') as token:
              token.write(creds.to_json())
        service = build('sheets', 'v4', credentials=creds)
        self.sheet = service.spreadsheets()

    # returns a 2D array consisting of the spreadsheet content
    def get_data(self):
        result = self.sheet.values().get(
          spreadsheetId=self.spreadsheet_id,
          range=config.RANGE).execute()
        values = result.get('values', [])
        values = [[i.strip() for i in j] for j in values]
        return values
