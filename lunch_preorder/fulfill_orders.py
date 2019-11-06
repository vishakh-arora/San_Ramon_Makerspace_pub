from __future__ import print_function
from guizero import App, Text, TextBox
# Work with Python 3.6
#from PIL import Image
from googleapiclient.discovery import build
from httplib2 import Http
from oauth2client import file, client, tools
from google.oauth2 import service_account
from operator import itemgetter
import random
import string
import sys, time, os.path
import googleapiclient.discovery
import html
#import smtplib
#from email.mime.multipart import MIMEMultipart
#from email.mime.base import MIMEBase
#from email.mime.text import MIMEText
#from email.mime.image import MIMEImage
#from email import encoders
#import barcode
#import barcode
#import datetime
#from barcode.writer import ImageWriter
#import imghdr
#import os

#pswd = open('pswd.txt','r').read().split('\n')
#print(pswd)
#gmail_user = pswd[0]
#gmail_password = pswd[1]


# If modifying these scopes, delete the file token.json.
SCOPES = ['https://www.googleapis.com/auth/spreadsheets']

SAMPLE_SPREADSHEET_ID ='1VYPZ9BLC4IN0wXlMcDLKpsoZC5o7GlcFy3Y0f_XkQAs'
#SAMPLE_SPREADSHEET_ID ='1wVxCCt75JyoL8N6wDT2YDNbK9411esNolWUWyHJ9T5g'
SAMPLE_RANGE_NAME = 'Lunch_preorders!A2:R'
#SAMPLE_RANGE_NAME = 'Locker_Responses!A2:I'
ORDER_SPREADSHEET_ID = '1HBJ4ES21BtVONE_fXGlCRR7i_Jx2ezqluehfeaY1Rr4'
ORDER_READ_RANGE = 'Orders!A2:D'
WRITING_RANGE_RESPONSES = 'Lunch_preorders!Q2:Z'
WRITING_RANGE = 'Orders!A2:Z'
#UNASSIGNED_LOCKERS_RANGE = 'Unassigned_Lockers!A2:B'
VALUE_INPUT_OPTION = "RAW"

SERVICE_ACCOUNT_FILE = 'service.json'
#=======

COL_ORDER_DATE = -1
COL_CARTE_OR_NO = 2
COL_EMAIL_ADDRESS = 1
COL_ORDERID = 3
BEGIN_ENTREE = 5
END_ENTREE = 15
COL_SIDE = 2
COL_ENTREE = 1
COL_DONE = 17

"""Shows basic usage of the Sheets API.
Prints values from a sample spreadsheet.
"""
# The file token.json stores the user's access and refresh tokens, and is
# created automatically when the authorization flow completes for the first
# time.

path = os.path.dirname(sys.argv[0])
store = file.Storage('token.json')
creds = store.get()
if not creds or creds.invalid:
    creds = service_account.Credentials.from_service_account_file( path + "/" +SERVICE_ACCOUNT_FILE, scopes=SCOPES)
    service = build('sheets', 'v4', credentials=creds)

# Call the Sheets API
sheet = service.spreadsheets()
result = sheet.values().get(spreadsheetId=ORDER_SPREADSHEET_ID,
                            range=ORDER_READ_RANGE).execute()
values = result.get('values')

orderID_index = {}

for i in range(len(values)):
  print(values[i][COL_ENTREE])
  orderID_index[values[i][COL_ORDERID]] = i

def getOrder(orderID):
  rowIndex = orderID_index.get(str(orderID))
  meal = ""
  if (rowIndex == None):
    return "Order ID "+str(orderID)+" not found"
  entree = html.escape(values[rowIndex][COL_ENTREE],quote=True)
  print(entree)
  side = html.escape(values[rowIndex][COL_SIDE],quote=True)
  if (side != ''):
    meal = "Entree: "+entree+"<br>Side: "+side
  else:
    meal = "Entree: "+entree
  return meal
