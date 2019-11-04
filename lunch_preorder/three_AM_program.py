from __future__ import print_function
from get_orders import copy_orders
# Work with Python 3.6

from PIL import Image
from googleapiclient.discovery import build
from httplib2 import Http
from oauth2client import file, client, tools
from google.oauth2 import service_account
from operator import itemgetter
import random
import string
import sys
import googleapiclient.discovery
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email.mime.text import MIMEText
from email.mime.image import MIMEImage
from email import encoders
import barcode
import barcode
import datetime
from barcode.writer import ImageWriter
import imghdr
import os

pswd = open('pswd.txt','r').read().split('\n')
#print(pswd)
gmail_user = pswd[0]
gmail_password = pswd[1]


# If modifying these scopes, delete the file token.json.
SCOPES = ['https://www.googleapis.com/auth/spreadsheets']

SAMPLE_SPREADSHEET_ID ='1VYPZ9BLC4IN0wXlMcDLKpsoZC5o7GlcFy3Y0f_XkQAs'
RPI_SPREADSHEET_ID = '1HBJ4ES21BtVONE_fXGlCRR7i_Jx2ezqluehfeaY1Rr4'
#SAMPLE_SPREADSHEET_ID ='1wVxCCt75JyoL8N6wDT2YDNbK9411esNolWUWyHJ9T5g'
SAMPLE_RANGE_NAME = 'Lunch_preorders!A2:R'
RPI_RANGE = 'Orders!A2:E'
#SAMPLE_RANGE_NAME = 'Locker_Responses!A2:I'
ORDER_SPREADSHEET_ID = '1HBJ4ES21BtVONE_fXGlCRR7i_Jx2ezqluehfeaY1Rr4'
WRITING_RANGE_RESPONSES = 'Lunch_preorders!A2:Z'
WRITING_RANGE = 'Orders!A2:Z'
#UNASSIGNED_LOCKERS_RANGE = 'Unassigned_Lockers!A2:B'
VALUE_INPUT_OPTION = "RAW"


#NUM_STUDENTS = 3500

SERVICE_ACCOUNT_FILE = 'service.json'
#=======

COL_ORDER_DATE = 0
COL_CARTE_OR_NO = 2
COL_EMAIL_ADDRESS = 1
COL_ORDERID = 16
BEGIN_ENTREE = 5
END_ENTREE = 15
COL_SIDE = -1
COL_ENTREE = -1
COL_DONE = 17
COL_KEY = 4

"""Shows basic usage of the Sheets API.
Prints values from a sample spreadsheet.
"""
# The file token.json stores the user's access and refresh tokens, and is
# created automatically when the authorization flow completes for the first
# time.
store = file.Storage('token.json')
creds = store.get()
if not creds or creds.invalid:
    creds = service_account.Credentials.from_service_account_file( SERVICE_ACCOUNT_FILE, scopes=SCOPES)
    service = build('sheets', 'v4', credentials=creds)

# Call the Sheets API
sheet = service.spreadsheets()
result = sheet.values().get(spreadsheetId=SAMPLE_SPREADSHEET_ID,
                            range=SAMPLE_RANGE_NAME).execute()
values = result.get('values')



copy_orders()

result_RPi = sheet.values().get(spreadsheetId=RPI_SPREADSHEET_ID,
                            range=RPI_RANGE).execute()
values_RPi = result_RPi.get('values')
updated_values_RPi = []
orderLogs = open("orderLogs.csv","a")
orderLog = ""
today = datetime.datetime(2019,10,29,3)
today = today.strftime("%m")+"/"+today.strftime("%d")+"/"+today.strftime("%Y")
print("TODAY = "+today)
for i in values_RPi:
    if (i[COL_ORDER_DATE] != today):
        for j in range(len(i)-1):
            orderLog += "\""+i[j]+"\","
        orderLog = orderLog[:-1] + "\n"
    elif (i[COL_ORDER_DATE] == today):
        updated_values_RPi.append(i)
print(orderLog)
print(updated_values_RPi)
orderLogs.write(orderLog)
orderLogs.close()

def clearResponses():
    valuesEmpty = []
    for i in values:
        vals = []
        for j in i:
            vals.append('')
        valuesEmpty.append(vals)

    body = {'values': valuesEmpty}
    result = service.spreadsheets().values().update(
    spreadsheetId=SAMPLE_SPREADSHEET_ID, range=WRITING_RANGE_RESPONSES,
    valueInputOption=VALUE_INPUT_OPTION, body=body).execute()

    valuesEmpty_RPi = []
    for i in values_RPi:
        vals = []
        for j in i:
            vals.append('')
        valuesEmpty_RPi.append(vals)

    body = {'values': valuesEmpty_RPi}
    result = service.spreadsheets().values().update(
    spreadsheetId=RPI_SPREADSHEET_ID, range=WRITING_RANGE,
    valueInputOption=VALUE_INPUT_OPTION, body=body).execute()

print(values)
clearResponses()
rowsToRetain = []
for i in values:
    if (i[COL_DONE] != "Done"):
        rowsToRetain.append(i)
print("ROWS TO RETAIN")
print(rowsToRetain)
orderSummary = {}
for i in updated_values_RPi:
    orderSummary[i[COL_KEY]] = 0
for i in updated_values_RPi:
    orderSummary[i[COL_KEY]] += 1

ordersCSV = "Order,Count"

for i in orderSummary:
    ordersCSV += ",\n"+"\""+i+"\","+str(orderSummary[i])


today = datetime.datetime.now()
date_formatted = today.strftime("%Y")+"-"+today.strftime("%m")+"-"+today.strftime("%d")
fname = "orderSummary_"+date_formatted+".csv"
fout = open(fname,"w")
fout.write(ordersCSV)
fout.close()

def mail(to, subject, text=None, attach=None):
   msg = MIMEMultipart()

   msg['From'] = gmail_user
   msg['To'] = to
#','.split(to)
   msg['Subject'] = subject
   if text != None:
   	msg.attach(MIMEText(text))
   if attach != None:
       part = MIMEBase('application', "octet-stream")
       part.set_payload(open(attach, "rb").read())
       encoders.encode_base64(part)
       part.add_header('Content-Disposition', 'attachment', filename=attach)  # or
       msg.attach(part)
	   # part = MIMEBase('application', 'octet-stream')
	   # part.set_payload(open(attach, 'rb').read())
	   # encoders.encode_base64(part)
	   # part.add_header('Content-Disposition', 'attachment; filename="%s"' % os.path.basename(attach))
	   # msg.attach(part)

#TODO: CHANGE TO LINODE SMTP CLIENT
   mailServer = smtplib.SMTP("smtp.gmail.com", 587)
   mailServer.ehlo()
   mailServer.starttls()
   #mailServer.ehlo()
   mailServer.login(gmail_user, gmail_password)
   mailServer.sendmail(gmail_user, to, msg.as_string())
   # Should be mailServer.quit(), but that crashes...
   mailServer.close()

def generate_email():
    # try:
    #     server = smtplib.SMTP_SSL('smtp.gmail.com', 465)
    #     server.ehlo()
    #     server.login(gmail_user, gmail_password)
    # except Exception as e:
    #     print(e)

    sent_from = gmail_user
    #to = "scurry@srvusd.net"
    to = "vishakh.arora29@gmail.com"
    subject = "Lunch Preorder Summary for "+date_formatted

    body = 'Dear Ms. Curry,\n' + \
        '\n' + \
        'Please find attached a csv file with the order summary for today. The most commonly ordered items (the ones with the highest count) will need to be prepared prior to lunch.\n' + \
        '\n' + \
        'Thanks,\n' + \
        'San Ramon Makerspace'

    try:
        mail(to, subject, body, fname)

    except Exception as e:
        print("ERROR: Failed to send email to: "+to+": "+str(e))


body = {'values': updated_values_RPi}
result = service.spreadsheets().values().update(
spreadsheetId=RPI_SPREADSHEET_ID, range=WRITING_RANGE,
valueInputOption=VALUE_INPUT_OPTION, body=body).execute()

body = {'values': rowsToRetain}
result = service.spreadsheets().values().update(
spreadsheetId=SAMPLE_SPREADSHEET_ID, range=WRITING_RANGE_RESPONSES,
valueInputOption=VALUE_INPUT_OPTION, body=body).execute()

generate_email()
