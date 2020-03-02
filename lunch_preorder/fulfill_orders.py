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
import html, datetime
from timeloop import Timeloop
import datetime


# If modifying these scopes, delete the file token.json.
SCOPES = ['https://www.googleapis.com/auth/spreadsheets']

SAMPLE_RANGE_NAME = 'Lunch_preorders!A2:R'
#SAMPLE_RANGE_NAME = 'Locker_Responses!A2:I'
ORDER_SPREADSHEET_ID = '1NgjQHMw1JGcOpHOTW4rdviKrCOEslBRfz-KZ3KfJcaQ'
ORDER_READ_RANGE = 'Orders!A2:D'
VALUE_INPUT_OPTION = "RAW"
TIMESTAMP_ID = "1PLY2nDpAr1OLdWsPRGfqiJMt9FcOt5eviH1B3jVUlSs"
TIMESTAMP_RANGE = "Timestamps!A2:B"

#SERVICE_ACCOUNT_FILE = '/Users/vishakh/Documents/11th Grade/Lunch_preordering/preorder_service.json'
#=======

COL_ORDER_DATE = 0
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
orderID_index = {}
INSTALL_PATH = '/home/pi/San_Ramon_Makerspace/lunch_preorder/'

# os.path.dirname(sys.argv[0])
values = []
SERVICE_ACCOUNT_FILE = INSTALL_PATH + '/preorder_service.json'

def getService():
  print(SERVICE_ACCOUNT_FILE)
  store = file.Storage('token.json')
  creds = store.get()
  if not creds or creds.invalid:
    creds = service_account.Credentials.from_service_account_file( SERVICE_ACCOUNT_FILE, scopes=SCOPES)
    service = build('sheets', 'v4', credentials=creds)
  return service

dict_timestamp = {}

def indexOrders( new_values):
  global orderID_index
  global values

  new_index = {}
  for i in range(len(new_values)):
    new_index[ new_values[i][COL_ORDERID]] = i
  values = new_values
  orderID_index = new_index

def reload(): #write to the spreadsheet here with timestamps
  # Call the Sheets API
  service = getService()
  sheet = service.spreadsheets()
  result = sheet.values().get(spreadsheetId=ORDER_SPREADSHEET_ID,
            range=ORDER_READ_RANGE).execute()
  new_values = result.get('values')
  indexOrders( new_values)
  print( "Orders read from sheet")
  save_file( new_values, getOrdersFilename(), "w")
  # Return the date so that user knows date of the data
  return new_values[0][COL_ORDER_DATE]

def getOrdersFilename():
  date = datetime.datetime.now()
  return INSTALL_PATH + date.strftime("orders_%Y-%m-%d.csv")

def refreshFile():
  print('Loading from local file')
  new_values = open( getOrdersFilename(), "r").read().strip().split("\n")

  print( "Orders read from local file")
  if (len(new_values) == 0):
    raise ValueError('No orders for today')

  for i in range(len(new_values)):
    new_values[i] = new_values[i].split("|")

  indexOrders( new_values)
  return new_values[0][COL_ORDER_DATE]

def save_file( data, fname, mode = "w"):
  # The file will not be written if reload is unable to contact
  print("Saving locally")
  fout = open( fname, mode)
  orders = ""
  for row in data:
    for col in range(len(row)):
      orders += row[col]
      if ( col != len(row) - 1):
        orders += "|"
    orders += "\n"
  fout.write(orders)
  fout.close()

def getOrder(orderID):
  orderID = str(orderID)[:12]
  rowIndex = orderID_index.get(orderID)
  meal = ""
  if (rowIndex == None):
    return "Order ID "+orderID+" not found"
  elif (dict_timestamp.get(orderID) == None):
#    return "Order ID "+orderID+" already served"
      # Get the timestamp in milliseconds, convert to string to prepare for writing to the spreadsheet
      print('Writing timestamp for ' + orderID)
      dict_timestamp[orderID] = [str(int(datetime.datetime.now().timestamp()*1000))]
  entree = html.escape(values[rowIndex][COL_ENTREE],quote=True)
  print(entree)
  side = html.escape(values[rowIndex][COL_SIDE],quote=True)
  if (side != ''):
    meal = "Entree: "+entree+"<br>Side: "+side
  else:
    meal = "A la Carte Entree: "+entree
  return meal

def construct_timestamps():

  # 2D array containing orders not saved 
  vals_timestamp = []
  order_ts_snapshot = dict_timestamp
  orders = list(order_ts_snapshot.keys())
  print("ORDER_TS_SNAPSHOT SPREADSHEET")
  print(order_ts_snapshot)  
  print( "Orders: " + str(len(orders)))
  for order in orders:
    timestamp_arr = []
    print("Checking marked:" + str(len(order_ts_snapshot[ order])))
    # if the order has not been already saved
    if (len(order_ts_snapshot[ order]) == 1):
      # Create a row with order id and it's timestamp
      timestamp_arr.append( order)
      timestamp_arr.append(order_ts_snapshot[order][0])
      # append the row
      vals_timestamp.append(timestamp_arr)
  print("TIMESTAMPS TO WRITE")
  print(vals_timestamp)
  #time.sleep(4)
  return vals_timestamp

def getTimestampsFilename():
  return INSTALL_PATH + "order_timestamps.csv"

def write_timestamp():
  print("WRITING TIMESTAMPS")
  timestamps = construct_timestamps()
  numUpdated = len( timestamps)
  save_file( timestamps, getTimestampsFilename(), "a")
  try:
    body = {'values': timestamps}
    service = getService()  
    result = service.spreadsheets().values().append(
    spreadsheetId=TIMESTAMP_ID, range=TIMESTAMP_RANGE,
    valueInputOption=VALUE_INPUT_OPTION, body=body).execute()
    numUpdated = result.get('updates').get('updatedCells')
  except Exception as e:
    print('Unable to write to Google sheet')
  mark_stamps(timestamps)
  return numUpdated


def mark_stamps(timestamp_vals):
  global dict_timestamp
  for order_ts_row in timestamp_vals:
    dict_timestamp[ order_ts_row[0]].append("WRITTEN")

def cron_write_timestamps(onoff):
#  timer = threading.Timer(300.0,write_timestamp)
  tl = Timeloop()
  @tl.job(interval=datetime.timedelta(seconds=20))
  def write_times():
    write_timestamp()
  if (onoff == 'on'):
    tl.start()
    print ("Timer started")
    return ("Timer started")
  elif (onoff == 'off'):
    tl.stop()
    print ("Timer cancelled")
    return ("Timer cancelled")

if len(sys.argv) > 1 and sys.argv[1] == "save":
    try:
        reload()
    except:
        refreshFile()
if len(sys.argv) > 1 and sys.argv[1] == "time":
   write_timestamp()
