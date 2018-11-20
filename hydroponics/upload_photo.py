#!/usr/bin/python
# https://developers.google.com/drive/api/v3/quickstart/python?refresh=1&pli=1
# pip install oauth2client
# pip install google-api-python-client

# Run this via
# python upload_photo.py --noauth_local_webserver
# Use the browser to authenticate the use

import requests
import json
import google.auth
from apiclient.discovery import build
from oauth2client import file, client, tools
from google.oauth2 import service_account

def get_service(key_file_location):
# Setup the Photo v1 API
    SCOPES = 'https://www.googleapis.com/auth/photoslibrary'
    store = file.Storage('credentials.json')
    creds = store.get()
    if not creds or creds.invalid:
        flow = client.flow_from_clientsecrets(key_file_location, SCOPES)
        creds = tools.run_flow(flow, store)
    # creds = ServiceAccountCredentials.from_json_keyfile_name(key_file_location)
    # creds = service_account.Credentials.from_service_account_file( key_file_location, scopes=SCOPES)
    service = build('photoslibrary', 'v1', credentials=creds)
    return service

def upload(service, file):
    f = open(file, 'rb').read();

    url = 'https://photoslibrary.googleapis.com/v1/uploads'
    headers = {
        'Authorization': "Bearer " + service._http.request.credentials.access_token,
        'Content-Type': 'application/octet-stream',
        'X-Goog-Upload-File-Name': file,
        'X-Goog-Upload-Protocol': "raw",
    }

    r = requests.post(url, data=f, headers=headers)
    #print('\nUpload token: %s' % r.content)
    return r.content

def createItem(service, upload_token, description, albumId):
    url = 'https://photoslibrary.googleapis.com/v1/mediaItems:batchCreate'

    body = {
        'newMediaItems' : [
	{
	    "description": description,
	    "simpleMediaItem": {
		"uploadToken": upload_token.decode('utf-8')
	    }
	}
        ]
    }

    if albumId is not None:
        body['albumId'] = albumId;

    #print(body)
    bodySerialized = json.dumps(body);
    headers = {
        'Authorization': "Bearer " + service._http.request.credentials.access_token,
        'Content-Type': 'application/json',
    }

    r = requests.post(url, data=bodySerialized, headers=headers)
    print('\nCreate item response: %s' % r.content)
    return r.content;

#authenticate user and build service
albumId=None
key_file_location='makerspace_oauth_secret.json'
service=get_service( key_file_location)
upload_token = upload(service, './plant.jpg')
response = createItem(service,upload_token, 'lettuce_seeds', albumId)
