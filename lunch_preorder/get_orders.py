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

#pswd = open('/home/vishakh/pswd.txt','r').read().split('\n')
#print(pswd)
#gmail_user = pswd[0]
#gmail_password = pswd[1]
from_user = "do-not-reply@srvusd-lunch.com"

# If modifying these scopes, delete the file token.json.
SCOPES = ['https://www.googleapis.com/auth/spreadsheets']

#SAMPLE_SPREADSHEET_ID ='1aD6FpWSCD7yD0RlpSDh0qdP4oaCPPDYpT48AfaVl6QY'
#SAMPLE_SPREADSHEET_ID ='1wVxCCt75JyoL8N6wDT2YDNbK9411esNolWUWyHJ9T5g'
SAMPLE_SPREADSHEET_ID = '1VYPZ9BLC4IN0wXlMcDLKpsoZC5o7GlcFy3Y0f_XkQAs'
#SAMPLE_RANGE_NAME = 'Locker_Responses!A2:I'
ORDER_SPREADSHEET_ID = '1NgjQHMw1JGcOpHOTW4rdviKrCOEslBRfz-KZ3KfJcaQ'
WRITING_RANGE_RESPONSES = 'Lunch_preorders!Q2:Z'
ROW_START_RANGE = 'Lunch_preorders!R2:R'
WRITING_RANGE = 'Orders!A2:Z'
#UNASSIGNED_LOCKERS_RANGE = 'Unassigned_Lockers!A2:B'
VALUE_INPUT_OPTION = "RAW"


#NUM_STUDENTS = 3500

SERVICE_ACCOUNT_FILE = '/home/vishakh/preorder_service.json'
#=======

COL_ORDER_DATE = -1
COL_CARTE_OR_NO = 2
COL_EMAIL_ADDRESS = 1
COL_ORDERID = 16
BEGIN_ENTREE = 5
END_ENTREE = 15
COL_SIDE = -1
COL_ENTREE = -1
COL_DONE = 17

"""Shows basic usage of the Sheets API.
Prints values from a sample spreadsheet.
"""
# The file token.json stores the user's access and refresh tokens, and is
# created automatically when the authorization flow completes for the first
# time.
store = file.Storage('token.json')
creds = store.get()
if not creds or creds.invalid:
    print("Getting authorization")
    creds = service_account.Credentials.from_service_account_file( SERVICE_ACCOUNT_FILE, scopes=SCOPES)
#    print(str(creds))
    service = build('sheets', 'v4', credentials=creds)

# Call the Sheets API
sheet = service.spreadsheets()
row_start = sheet.values().get(spreadsheetId=SAMPLE_SPREADSHEET_ID,
                            range=ROW_START_RANGE).execute()
start_index = int(row_start.get('values')[0][0])
SAMPLE_RANGE_NAME = 'Lunch_preorders!A'+str(start_index+2)+':Q'
result = sheet.values().get(spreadsheetId=SAMPLE_SPREADSHEET_ID,
                            range=SAMPLE_RANGE_NAME).execute()
values = result.get('values')
done_values = []
# for i in values:
#     i.append("ORDERID")
#counter = 1
#vals_no_blanks = []
#for i in values:
#  if (len(i) != 0):
#    vals_no_blanks.append(i)
#    print(i)
##  else:
#    print(str(counter))
#    print(i)
#  counter += 1
#values = vals_no_blanks
#
order_copies = []
#print(str(counter))
print(values)

def getEntreeSide(row):
    global COL_SIDE
    global COL_ENTREE
    global values

    for j in range(BEGIN_ENTREE,END_ENTREE+1):
        if (row[j] != ""):
            COL_ENTREE = j
            COL_SIDE = j + 1
            break

def getMaxID():
    maxID = 1
    for i in values:
        if (i[COL_ORDERID] != 'Placeholder'):
            print(i)
            orderID = int(i[COL_ORDERID][:-4])
            print(orderID)
            if (orderID > maxID):
                maxID = orderID
    return maxID

def create_orderID(i, counter):
    global COL_ORDER_DATE
    global values

    if (i[3] != ''):
        COL_ORDER_DATE = 3
    elif (i[4] != ''):
        COL_ORDER_DATE = 4

    orderDate = i[COL_ORDER_DATE].split('/')
    print(orderDate)
    month = orderDate[0].zfill(2)
    day = orderDate[1].zfill(2)
    year = orderDate[2]
    orderID = year + day + month + str(counter).zfill(4)
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

def constructKey(row):
    getEntreeSide(row)

    if (row[COL_CARTE_OR_NO] == "No"):
        key = row[COL_ENTREE]+" with "+row[COL_SIDE]
    elif (row[COL_CARTE_OR_NO] == "Yes"):
        key = row[COL_ENTREE]
    return key

def copy_orders(values,order_copies):

    #date = datetime.datetime(2020,1,26,8)
    date = datetime.datetime.now()
    hours_from_epoch = (((date - datetime.datetime(1970, 1, 1)) / datetime.timedelta(seconds=1)))/3600
    print("RN HOURS FROM EPOCH")
    print(hours_from_epoch)

    print(date)
    counter = getMaxID()
    first_row = 0
    for order_num in range(len(values)):
        i = values[order_num]
        getEntreeSide(i)
        order_array = []

        if (i[3] != ''):
            print(i[3])
            COL_ORDER_DATE = 3
        elif (i[4] != ''):
            COL_ORDER_DATE = 4
#        print("DATEEEEEEEEEEEEEEEEEEEEEEEEEEE")
 #       print(i[COL_ORDER_DATE])
        formatted_date = i[COL_ORDER_DATE].split('/')
        orderDate = datetime.datetime(int(formatted_date[2]),int(formatted_date[0]),int(formatted_date[1]))

        # Standardize order date so that date comparison works at 3 AM (10/9/19 --> 10/09/19)
        for j in range(len(formatted_date)):
            formatted_date[j] = formatted_date[j].zfill(2)
        i[COL_ORDER_DATE] = "/".join(formatted_date)
   #     orders_to_remove = []

        hours_from_epoch_order = (((orderDate - datetime.datetime(1970, 1, 1)) / datetime.timedelta(seconds=1)))/3600
#        print("ORDER HOURS FROM EPOCH")
#        print(orderDate)
#        print(abs(hours_from_epoch - hours_from_epoch_order))
        diff_hrs = hours_from_epoch - hours_from_epoch_order

        if (abs(diff_hrs) <= 24): # and i[COL_DONE] != 'Done'):
#            print(abs(hours_from_epoch - hours_from_epoch_order))
            print("CONSTRUCTING ORDER")
            orderID = create_orderID(i,counter)
            counter += 1
            i[COL_ORDERID] = orderID

            generate_email(i)
            for x in range(COL_ORDER_DATE,len(i)-1):
                order_array.append(i[x])

            order_array = remove_blanks(order_array)
            key = constructKey(i)
            if (i[COL_CARTE_OR_NO] == "Yes"):
                order_array.insert(2,'')
            order_array.append(key)
            order_array.append(i[COL_EMAIL_ADDRESS])
            order_array.insert(3,i[COL_ORDERID])
            print(order_array)
            order_copies.append(order_array)
#            i[COL_DONE] = "Done"
            print(i)
        elif (first_row == 0 and diff_hrs < 0):
            first_row = order_num + start_index
#            orders_to_remove.append(i)
 #   print("ORDERS TO REMOVE")
  #  print(orders_to_remove)
    # for h in orders_to_remove:
    #     values.remove(h)
    body = {'values': [[str(first_row)]]}
    result = service.spreadsheets().values().update(
    spreadsheetId=SAMPLE_SPREADSHEET_ID, range=ROW_START_RANGE,
    valueInputOption=VALUE_INPUT_OPTION, body=body).execute()
    #print(values)

    body = {'values': order_copies}
    result = service.spreadsheets().values().append(
    spreadsheetId=ORDER_SPREADSHEET_ID, range=WRITING_RANGE,
    valueInputOption=VALUE_INPUT_OPTION, body=body).execute()


def mail(to, subject, text=None, html=None, attach=None):
   msg = MIMEMultipart()
   msg['From'] = from_user #gmail_user
   msg['To'] = to
#','.split(to)
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
   #mailServer.ehlo()
#   mailServer.login(gmail_user, gmail_password)
   mailServer.sendmail(from_user, to, msg.as_string())
   # Should be mailServer.quit(), but that crashes...
   mailServer.close()

# Takes html input and replaces all <br> with \n
# removes all other html tags
def strip_html(text):
    text = text.replace("<br>","\n")
    text = re.sub(r'<[a-z/=\" -:0-9A-Z+;]*>',"",text)
    return text

def generate_email(vals):
    sent_from = from_user

    i = vals
    to = i[COL_EMAIL_ADDRESS]
    orderID = i[COL_ORDERID]

    subject = "Your Lunch Order for "+i[COL_ORDER_DATE]

    meal = i[COL_ENTREE]

    if (COL_SIDE != -1):
        meal = constructKey(i)
    orderID_fname = get_barcode_image( orderID)
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


def createResponsesWrite():
    global done_values

    for i in values:
        vals = []
        vals.append(i[COL_ORDERID])
        vals.append(i[COL_DONE])
        done_values.append(vals)
    print(done_values)
    return done_values

def main():
    copy_orders(values,order_copies)
    #print(values)

    print(order_copies)

if (__name__=='__main__'):
    main()
