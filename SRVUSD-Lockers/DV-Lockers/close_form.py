from __future__ import print_function
import googleapiclient.discovery

from PIL import Image
from googleapiclient.discovery import build
from httplib2 import Http
from oauth2client import file, client, tools
from google.oauth2 import service_account

SCOPES = ['https://www.googleapis.com/auth/forms']

SERVICE_ACCOUNT_FILE = 'service.json'

store = file.Storage('token.json')
creds = store.get()
if not creds or creds.invalid:
    creds = service_account.Credentials.from_service_account_file( SERVICE_ACCOUNT_FILE, scopes=SCOPES)
    service = build('script', 'v1', credentials=creds)

form = FormApp.openById('1ADsc5n5OCY1A3lXjdzPajKR4IYIIN4kXWbdh-Tp2cic');
form.setAcceptingResponses(false)
