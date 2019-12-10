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
import os

pswd = open('pswd.txt','r').read().split('\n')
#print(pswd)
gmail_user = pswd[0]
gmail_password = pswd[1]


# If modifying these scopes, delete the file token.json.
SCOPES = ['https://www.googleapis.com/auth/spreadsheets']

SAMPLE_SPREADSHEET_ID ='1VYPZ9BLC4IN0wXlMcDLKpsoZC5o7GlcFy3Y0f_XkQAs'
#SAMPLE_SPREADSHEET_ID ='1wVxCCt75JyoL8N6wDT2YDNbK9411esNolWUWyHJ9T5g'
SAMPLE_RANGE_NAME = 'Lunch_preorders!A2:R'
#SAMPLE_RANGE_NAME = 'Locker_Responses!A2:I'
ORDER_SPREADSHEET_ID = '1HBJ4ES21BtVONE_fXGlCRR7i_Jx2ezqluehfeaY1Rr4'
WRITING_RANGE_RESPONSES = 'Lunch_preorders!Q2:Z'
WRITING_RANGE = 'Orders!A2:Z'
#UNASSIGNED_LOCKERS_RANGE = 'Unassigned_Lockers!A2:B'
VALUE_INPUT_OPTION = "RAW"


#NUM_STUDENTS = 3500

SERVICE_ACCOUNT_FILE = 'preorder_service.json'
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
    print(str(creds))
    service = build('sheets', 'v4', credentials=creds)

# Call the Sheets API
sheet = service.spreadsheets()
result = sheet.values().get(spreadsheetId=SAMPLE_SPREADSHEET_ID,
                            range=SAMPLE_RANGE_NAME).execute()
values = result.get('values')
print(values)
done_values = []
# for i in values:
#     i.append("ORDERID")

orderid_fname = 0

order_copies = []

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
        if (i[COL_ORDERID] != ''):
            orderID = int(i[COL_ORDERID][:-4])
            print(orderID)
            if (orderID > maxID):
                maxID = orderID
    return maxID

def create_orderID(i, counter):
    global orderid_fname
    global COL_ORDER_DATE
    global values

    if (i[3] != ''):
        COL_ORDER_DATE = 3
    elif (i[4] != ''):
        COL_ORDER_DATE = 4

    orderDate = i[COL_ORDER_DATE].split('/')
    #print(orderDate)
    month = orderDate[0].zfill(2)
    day = orderDate[1].zfill(2)
    year = orderDate[2]
    orderID = year + day + month + str(counter).zfill(4)

    foo = barcode.get('ean13', orderID, writer=ImageWriter())
    orderid_fname = orderID + '_' + str(values.index(i))
    filename = foo.save(orderid_fname)
    orderid_fname  = orderid_fname + '.png'

    return orderID

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

def copy_orders():
    global values

    #date = datetime.datetime.now()
    date = datetime.datetime(2019,11,6,17)
    hours_from_epoch = (((date - datetime.datetime(1970, 1, 1)) / datetime.timedelta(seconds=1)))/3600
    print(hours_from_epoch)

    print(date)
    counter = getMaxID()

    for i in values:
        getEntreeSide(i)
        order_array = []

        if (i[3] != ''):
            print(i[3])
            COL_ORDER_DATE = 3
        elif (i[4] != ''):
            COL_ORDER_DATE = 4

        formatted_date = i[COL_ORDER_DATE].split('/')
        orderDate = datetime.datetime(int(formatted_date[2]),int(formatted_date[0]),int(formatted_date[1]))

        # Standardize order date so that date comparison works at 3 AM (10/9/19 --> 10/09/19)
        for j in range(len(formatted_date)):
            formatted_date[j] = formatted_date[j].zfill(2)
        i[COL_ORDER_DATE] = "/".join(formatted_date)
        print("ORDER DATEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEE")
        print(i[COL_ORDER_DATE])
        orders_to_remove = []

        hours_from_epoch_order = (((orderDate - datetime.datetime(1970, 1, 1)) / datetime.timedelta(seconds=1)))/3600
        print(hours_from_epoch_order)
        if (abs(hours_from_epoch - hours_from_epoch_order) <= 24 and i[COL_DONE] == 'Placeholder'):
            print(abs(hours_from_epoch - hours_from_epoch_order))
            print("CONSTRUCTING ORDER")
            orderID = create_orderID(i,counter)
            counter += 1
            i[COL_ORDERID] = orderID

            generate_email(i)
            os.remove(orderid_fname)
            for x in range(COL_ORDER_DATE,len(i)-1):
                order_array.append(i[x])

            order_array = remove_blanks(order_array)
            key = constructKey(i)
            #order_array.insert(1,i[COL_ORDERID])
            if (i[COL_CARTE_OR_NO] == "Yes"):
                order_array.insert(2,'')
            order_array.append(key)
            order_array.append(i[COL_EMAIL_ADDRESS])
            print(order_array)
            order_copies.append(order_array)
            i[COL_DONE] = "Done"
            print(i)
            orders_to_remove.append(i)
    print("ORDERS TO REMOVE")
    print(orders_to_remove)
    # for h in orders_to_remove:
    #     values.remove(h)
    #print(values)


def mail(to, subject, text=None, attach=None):
   msg = MIMEMultipart()

   msg['From'] = gmail_user
   msg['To'] = to
#','.split(to)
   msg['Subject'] = subject
#   if text != None:
#  	  msg.attach(MIMEText(text,'html'))

   if attach != None:
       msgAlternative = MIMEMultipart('alternative')
       msg.attach(msgAlternative)

#       msgText = MIMEText('<br><img src="cid:image1"><br>', 'html')
#       msgAlternative.attach(msgText)

       msgAlternative.attach(MIMEText(text, 'html'))

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

#TODO: CHANGE TO LINODE SMTP CLIENT
   mailServer = smtplib.SMTP("smtp.gmail.com", 587)
   mailServer.ehlo()
   mailServer.starttls()
   #mailServer.ehlo()
   mailServer.login(gmail_user, gmail_password)
   mailServer.sendmail(gmail_user, to, msg.as_string())
   # Should be mailServer.quit(), but that crashes...
   mailServer.close()


def generate_email(vals):
    # try:
    #     server = smtplib.SMTP_SSL('smtp.gmail.com', 465)
    #     server.ehlo()
    #     server.login(gmail_user, gmail_password)
    # except Exception as e:
    #     print(e)

    sent_from = gmail_user

    i = vals
    to = i[COL_EMAIL_ADDRESS]

    subject = "Lunch Preorder Barcode"

    meal = i[COL_ENTREE]

    if (COL_SIDE != -1):
        meal = constructKey(i)

    body = 'Dear student,<br>' + \
        '<br>' + \
        'Thank you for participating in the lunch preordering system. Here is the lunch that we got from you:<br>' + \
        '<b>Meal:</b> '+ meal + \
        '<br>' + \
        'Please find attached a file with a barcode. Show this barcode to the lunch worker serving you to receive your meal.<br>' + \
        '<br><img src="cid:image1"><br>' + \
        '<b>PLEASE NOTE</b>: If your meal was not one of the most commonly preordered items, your meal will need to be packaged on the spot (similar to the process before, except your order is already known).<br>' + \
        '<br>' + \
        'Thanks,<br>' + \
        'San Ramon Makerspace'

    try:
        mail(to, subject, body, orderid_fname)

    except Exception as e:
        print("ERROR: Failed to send email to: "+to+": "+str(e))


    #server.close()
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
    copy_orders()
    #print(values)
    body = {'values': createResponsesWrite()}
    result = service.spreadsheets().values().update(
    spreadsheetId=SAMPLE_SPREADSHEET_ID, range=WRITING_RANGE_RESPONSES,
    valueInputOption=VALUE_INPUT_OPTION, body=body).execute()

    print(order_copies)
    body = {'values': order_copies}
    result = service.spreadsheets().values().append(
    spreadsheetId=ORDER_SPREADSHEET_ID, range=WRITING_RANGE,
    valueInputOption=VALUE_INPUT_OPTION, body=body).execute()

if (__name__=='__main__'):
    main()
