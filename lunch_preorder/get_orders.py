#!/usr/bin/python3

################################################################################################
# runs every minute
# collect all orders, for every order that's for tomorrow create barcodes/send emails,
# copy over to RPi spreadsheet, delete from order spreadsheet
################################################################################################

# Work with Python 3.6
from __future__ import print_function
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
import datetime
from barcode.writer import ImageWriter
import imghdr
from io import BytesIO
import os
import re
import base64
import urllib
import requests

from_user = "do-not-reply@srvusd-lunch.com"

# If modifying these scopes, delete the file token.json.
SCOPES = ['https://www.googleapis.com/auth/spreadsheets']

#FORM_SPREADSHEET_ID ='1aD6FpWSCD7yD0RlpSDh0qdP4oaCPPDYpT48AfaVl6QY'
FORM_SPREADSHEET_ID = '1VYPZ9BLC4IN0wXlMcDLKpsoZC5o7GlcFy3Y0f_XkQAs'

ORDER_SPREADSHEET_ID = '1NgjQHMw1JGcOpHOTW4rdviKrCOEslBRfz-KZ3KfJcaQ'
ROW_STORE_RANGE = 'Lunch_preorders!R1:T1'
WRITING_RANGE = 'Orders!A2:Z'

VALUE_INPUT_OPTION = "RAW"

SERVICE_ACCOUNT_FILE = '/home/vishakh/preorder_service.json'

COL_ORDER_DATE = -1
COL_CARTE_OR_NO = 2
COL_EMAIL_ADDRESS = 1
COL_ORDERID = 16
BEGIN_ENTREE = 5
END_ENTREE = 15
COL_SIDE = -1
COL_ENTREE = -1
COL_DONE = 17

store = file.Storage('token.json')
creds = store.get()
if not creds or creds.invalid:
    print("Getting authorization")
    creds = service_account.Credentials.from_service_account_file( SERVICE_ACCOUNT_FILE, scopes=SCOPES)
    # print(str(creds))
    service = build('sheets', 'v4', credentials=creds)

def readData(service):
    sheet = service.spreadsheets()
    # Read any stored values of row values for start range and completed order row
    row_indices = sheet.values().get(spreadsheetId=FORM_SPREADSHEET_ID,
                                range=ROW_STORE_RANGE).execute()
    search_row = int(row_indices.get('values')[0][0])

    # Read data from the form spreadsheet
    readRange = 'Lunch_preorders!A'+str(search_row+2)+':Q'
    result = sheet.values().get(spreadsheetId=FORM_SPREADSHEET_ID,
                                range=readRange).execute()
    values = result.get('values')
    return (values, search_row)


def readState(service):
    sheet = service.spreadsheets()
    # Read any stored values of row values for start range and completed order row
    row_indices = sheet.values().get(spreadsheetId=FORM_SPREADSHEET_ID,
                                range=ROW_STORE_RANGE).execute()
    processed_row = int(row_indices.get('values')[0][1])
    order_ID = int(row_indices.get('values')[0][2])
    return (processed_row, order_ID)

def getEntreeSide(row):
    global COL_SIDE
    global COL_ENTREE

    for j in range(BEGIN_ENTREE,END_ENTREE+1):
        if (row[j] != ""):
            COL_ENTREE = j
            COL_SIDE = j + 1
            break

def create_orderID(row, counter, COL_ORDER_DATE):
    orderDate = row[COL_ORDER_DATE].split('/')
    #print(orderDate)
    month = orderDate[0].zfill(2)
    day = orderDate[1].zfill(2)
    year = orderDate[2]
    orderID = year + day + month + str(counter).zfill(4)
    row[COL_ORDERID] = orderID
#    print(orderID)
    return orderID

def get_barcode_image( orderID):
    foo = barcode.get('ean13', orderID, writer=ImageWriter())
    orderid_fname = foo.save(orderID)
    return orderid_fname

def remove_blanks(values):
    noBlanks = []
    for i in values:
        if (i != ""):
            noBlanks.append(i)
    print(noBlanks)
    return noBlanks

def constructMeal(row):
    getEntreeSide(row)

    if (row[COL_CARTE_OR_NO] == "No"):
        key = row[COL_ENTREE]+" with "+row[COL_SIDE]
    elif (row[COL_CARTE_OR_NO] == "Yes"):
        key = row[COL_ENTREE]
    return key

def setCOL_ORDER_DATE(row):
    COL_ORDER_DATE = -1
    if (row[3] != ''):
        COL_ORDER_DATE = 3
    elif (row[4] != ''):
        COL_ORDER_DATE = 4
    return COL_ORDER_DATE

def formatDate(date_arr):
    for j in range(len(date_arr)):
        date_arr[j] = date_arr[j].zfill(2)
    return "/".join(date_arr)

def constructOrderArray(row, COL_ORDER_DATE):
    order_array = []

    for x in range(COL_ORDER_DATE,len(row)-1):
        order_array.append(row[x])

    order_array = remove_blanks(order_array)
    meal = constructMeal(row)
    if (row[COL_CARTE_OR_NO] == "Yes"):
        order_array.insert(2,'')
    order_array.append(meal)
    order_array.append(row[COL_EMAIL_ADDRESS])
    order_array.insert(3,row[COL_ORDERID])

    return order_array
    #print(order_array)

def convertToDate(strDate):
    parts = strDate.split('/')
    date = datetime.datetime(int(parts[2]),int(parts[0]),int(parts[1]))
    return (date, parts)

def compareOrderDate(row, COL_ORDER_DATE, processing_date):
    orderDate, dateParts = convertToDate( row[COL_ORDER_DATE])
    # Standardize order date so that date comparison works at 3 AM (10/9/19 --> 10/09/19)
    row[COL_ORDER_DATE] = formatDate(dateParts)
    diff_days = (orderDate - processing_date)/ datetime.timedelta(seconds=1)/3600/24
    return int(diff_days)


def saveState( service, first_row, completed_row, order_ID):
    body = {'values': [[str(first_row), str(completed_row), str(order_ID)]]}
    result = service.spreadsheets().values().update(
    spreadsheetId=FORM_SPREADSHEET_ID, range=ROW_STORE_RANGE,
    valueInputOption=VALUE_INPUT_OPTION, body=body).execute()

def saveOrders( service, orders):
    body = {'values': orders}
    result = service.spreadsheets().values().append(
    spreadsheetId=ORDER_SPREADSHEET_ID, range=WRITING_RANGE,
    valueInputOption=VALUE_INPUT_OPTION, body=body).execute()

def rowOfHistoricalData( values, pdate):
    for row_num in range(len(values)):
        row = values[row_num]
        COL_ORDER_DATE = setCOL_ORDER_DATE(row)
        diff_days = compareOrderDate( row, COL_ORDER_DATE, pdate)
        if (diff_days >= 0):
            return row_num
    return row_num

def archive_orders( ):
    sheet = service.spreadsheets()
    result_RPi = sheet.values().get(spreadsheetId=ORDER_SPREADSHEET_ID,
                              range=WRITING_RANGE).execute()
    values_RPi = result_RPi.get('values')
    orderLogs = open("orderLogs.csv","a")
    for row in values_RPi:
          logline = ""
          for j in range(len(row)-1):
              logline += "\""+row[j]+"\","
          logline = logline[:-1] + "\n"
          orderLogs.write(logline.encode('utf-8'))
    orderLogs.close()

def delete_orders():
    requests = []
    requests.append( {
      "deleteDimension": {
        "range": {
          "sheetId": 0,
          "dimension": "ROWS",
          "startIndex": 1
        }
      }
    })
    body = {
      'requests': requests
    }
    response = service.spreadsheets().batchUpdate( spreadsheetId=ORDER_SPREADSHEET_ID, body=body).execute()

def startDay( processing_date):
    (values, start_index) = readData( service)
    # If we have never collected orders for this day, let's narrow down the top
    (pdate, x) = convertToDate( processing_date)
    earliest_row = rowOfHistoricalData( values, pdate)
    if (earliest_row > 0):
       print('Narrowed top row to: ' + str(start_index + earliest_row))
       saveState(service, start_index + earliest_row, -1, 0)
    archive_orders()
    delete_orders()

def processOrders( processing_date):
    (processed_row, counter) = readState( service)
    print('Number orders processed so far: ' + str(counter))
    (values, start_index) = readData( service)

    (pdate, x) = convertToDate( processing_date)
    print('Will ignore orders till: ' + str(processed_row))

    for row_num in range(len(values)):
        row = values[row_num]
        COL_ORDER_DATE = setCOL_ORDER_DATE(row)
        diff_days = compareOrderDate( row, COL_ORDER_DATE, pdate)
        save_orders = []
        # If the order is for the processing date, send the email to the student and copy the order to RPi spreadsheet
        if (diff_days == 0 and row_num > processed_row):
            print("Adding order")
            orderID = create_orderID( row,counter,COL_ORDER_DATE)
            order_array = constructOrderArray( row, COL_ORDER_DATE)
            save_orders.append(order_array)
            try:
                generate_email(order_array)
            except:
                print("Unable to send mail for ")
                print(order_array)
                return
            counter += 1
            processed_row = row_num
            # Save the state after each successful order
            # The start_index should NOT be changed intra-day & the processed_row and counter are reset at beginning of each day
    saveState(service, start_index, processed_row, counter)
    saveOrders( service, save_orders)
    # print(order_copies)
    return

def mail(to, subject, text=None, html=None, attach=None):
   msg = MIMEMultipart()
   msg['From'] = from_user
   msg['To'] = to
   msg['Subject'] = subject

   if (html != None and text != None):
       msgAlternative = MIMEMultipart('alternative')
       msg.attach(msgAlternative)
       msgAlternative.attach(MIMEText(html, 'html'))
       msgAlternative.attach(MIMEText(text, 'plain'))
   elif (html != None):
       msg.attach(MIMEText(html, 'html'))
   elif (text != None):
       msg.attach(MIMEText(text, 'plain'))

   if (attach != None):
       fp = open(attach, 'rb')
       msgImage = MIMEImage(fp.read())
       fp.close()

       msgImage.add_header('Content-ID', '<image1>')
       msg.attach(msgImage)
	   # part = MIMEBase('application', 'octet-stream')
	   # part.set_payload(open(attach, 'rb').read())
	   # encoders.encode_base64(part)
	   # part.add_header('Content-Disposition', 'attachment; filename="%s"' % os.path.basename(attach))
	   # msg.attach(part)

   mailServer = smtplib.SMTP("localhost", 587)
   mailServer.ehlo()
   mailServer.starttls()
   mailServer.sendmail(from_user, to, msg.as_string())
   # Should be mailServer.quit(), but that crashes...
   mailServer.close()

# Takes html input and replaces all <br> with \n
# removes all other html tags
def strip_html(text):
    text = text.replace("<br>","\n")
    text = re.sub(r'<[a-z/=\" -:0-9A-Z+;]*>',"",text)
    return text

COL_ORDER_DET_EMAIL = 5
COL_ORDER_DET_ID = 3
COL_ORDER_DET_DATE = 0
COL_ORDER_DET_MEAL = 4
def generate_email(order_array):
    sent_from = from_user

    to = order_array[COL_ORDER_DET_EMAIL]
    orderID = order_array[COL_ORDER_DET_ID]

    subject = "Your Lunch Order for "+order_array[COL_ORDER_DET_DATE]

    meal = order_array[COL_ORDER_DET_MEAL]

    orderID_fname = get_barcode_image(orderID)
    fp = open(orderID_fname, 'rb')
    data_uri = base64.b64encode(fp.read()).decode()
    fp.close()

     # The embedded image doesn't show up in gmail so use inline attachment
     # '<br>\n<img src="data:image/png;base64,{0}" alt="">'.format(data_uri) + \
    htmlbody = '<html><body>Dear Student,<br>' + \
        '<br>' + \
        '<b>This is a test of the lunch preordering system. You will not be scanning the barcdoe below to receive your meal at this stage.</b><br><br>' + \
        'Thank you for ordering through the lunch preordering system. Below are the details of your order:' + \
        '<br><b>Order ID:</b> '+ orderID + \
        '<br><b>Meal:</b> '+ meal + \
        '<br>Please find the barcode below that you can scan at the lunch station and pay using SchoolCafe to receive your meal.<br>' + \
        '<br>\n<img src="cid:image1" alt="order: ' + orderID + '">' + \
        '\n<br><b>PLEASE NOTE</b>: If your meal is not one of the most commonly preordered items, it will be packaged on the spot (similar to the process before, except your order is already known).<br>' + \
        '\n<br>Thanks,' + \
        '<br>San Ramon Makerspace</body></html>'
    textbody=strip_html( htmlbody)

    try:
        mail(to, subject, text=None, html=htmlbody, attach=orderID_fname)
        os.remove(orderID_fname)

    except Exception as e:
        print("ERROR: Failed to send email to: "+to+": "+str(e))

def start( date):
    orders = processOrders( date)

if (__name__=='__main__'):
    if (len(sys.argv) < 2):
        print('Requires a date in format mm/dd/yyyy')
        exit(2)
    date = sys.argv[1]
    if ( sys.argv < 3)
        processOrders( date)
    else if (sys.argv[2] == 'first_run')
        startDay( date)
