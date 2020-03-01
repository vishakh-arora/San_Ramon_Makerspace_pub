from __future__ import print_function

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
import datetime
import os

from_user = "do-not-reply@srvusd-lunch.com"

# If modifying these scopes, delete the file token.json.
SCOPES = ['https://www.googleapis.com/auth/spreadsheets']

RPI_SPREADSHEET_ID = '1NgjQHMw1JGcOpHOTW4rdviKrCOEslBRfz-KZ3KfJcaQ'
RPI_RANGE = 'Orders!A2:F'
WRITING_RANGE = 'Orders!A2:Z'
VALUE_INPUT_OPTION = "RAW"


SERVICE_ACCOUNT_FILE = '/home/vishakh/preorder_service.json'

COL_ORDER_DATE = 0
COL_CARTE_OR_NO = 2
COL_EMAIL_ADDRESS = 1
COL_ORDERID = 3
BEGIN_ENTREE = 5
END_ENTREE = 15
COL_SIDE = 2
COL_ENTREE = 1
COL_DONE = 17
COL_KEY = 4

store = file.Storage('token.json')
creds = store.get()
if not creds or creds.invalid:
  creds = service_account.Credentials.from_service_account_file( SERVICE_ACCOUNT_FILE, scopes=SCOPES)
  service = build('sheets', 'v4', credentials=creds)

def read_orders( process_date):
    sheet = service.spreadsheets()
    result_RPi = sheet.values().get(spreadsheetId=RPI_SPREADSHEET_ID,
                              range=RPI_RANGE).execute()
    values_RPi = result_RPi.get('values')
    updated_values_RPi = []
    for i in values_RPi:
      if (i[COL_ORDER_DATE] == process_date):
          updated_values_RPi.append(i)
    #print(updated_values_RPi)
    return (updated_values_RPi, len(values_RPi))

def clearResponses():
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

#clearResponses()

def mail(to, subject, text=None, attach=None, attach1=None):
   msg = MIMEMultipart()

   msg['From'] = from_user
   msg['To'] = ", ".join(to)
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
   if attach1 != None:
       part = MIMEBase('application', "octet-stream")
       part.set_payload(open(attach1, "rb").read())
       encoders.encode_base64(part)
       part.add_header('Content-Disposition', 'attachment', filename=attach1)  # or
       msg.attach(part)

   mailServer = smtplib.SMTP("localhost", 587)
   mailServer.ehlo()
   mailServer.starttls()
   #mailServer.ehlo()
#   mailServer.login(gmail_user, gmail_password)
   mailServer.sendmail(from_user, to, msg.as_string())
   # Should be mailServer.quit(), but that crashes...
   mailServer.close()

def generate_email():
    sent_from = from_user
    to = ["scurry@srvusd.net","lwhite@srvusd.net","vishakh.arora29@gmail.com"]
    #to = ["vishakh.arora29@gmail.com"] #,"parora12@gmail.com"]
    subject = "Lunch Preorder Summary for "+date_formatted

    body = 'Dear Ms. Curry and Ms. White,\n' + \
        '\n' + \
        'Please find attached two csv files with the entree and side summaries for today.\n' + \
        '\n' + \
        'Thanks,\n' + \
        'San Ramon Makerspace'
# The most commonly ordered items (the ones with the highest count) will need to be prepared prior to lunch.\n' + \

    try:
        mail(to, subject, body, fname_entree, fname_side)

    except Exception as e:
        print("ERROR: Failed to send email to: "+to+": "+str(e))


def summarize( data, column, summary_dict):
    for row in data:
        summary_dict[row[column]] = 0
    for row in data:
        summary_dict[row[column]] += 1

def construct_summary( header, data, column, fname):
    counts_dict = {}
    summarize( data, column, counts_dict)
    line = header
    for i in counts_dict:
        if (i != ""):
            line += ",\n"+"\""+i+"\","+str(counts_dict[i])
    fout = open(fname,"w")
    fout.write(line)
    fout.close()

today = datetime.datetime.now()
date_formatted = today.strftime("%Y")+"-"+today.strftime("%m")+"-"+today.strftime("%d")
process_date = today.strftime("%m")+"/"+today.strftime("%d")+"/"+today.strftime("%Y")
print(process_date)

(updated_values_RPi, numRows) = read_orders(process_date)
print(updated_values_RPi)
print(numRows)

fname_entree = "orderSummary_"+date_formatted+"_ENTREES.csv"
construct_summary( "Entree,Count", updated_values_RPi, COL_ENTREE, fname_entree)


fname_side = "orderSummary_"+date_formatted+"_SIDES.csv"
construct_summary( "Side,Count", updated_values_RPi, COL_SIDE, fname_side)

generate_email()
