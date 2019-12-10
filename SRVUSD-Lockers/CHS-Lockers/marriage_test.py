################################################################################################
# test marriage problem implementation form responses spreadsheet
################################################################################################


# Work with Python 3.6
from __future__ import print_function
from googleapiclient.discovery import build
from httplib2 import Http
from oauth2client import file, client, tools
from google.oauth2 import service_account
import googleapiclient.discovery


pswd = open('pswd.txt','r').read().split('\n')
#print(pswd)
gmail_user = pswd[0]
gmail_password = pswd[1]


# If modifying these scopes, delete the file token.json.
SCOPES = ['https://www.googleapis.com/auth/spreadsheets']

SAMPLE_SPREADSHEET_ID ='1nBTJnkp5oYT4UTJJXHgtp8maX7jAsjnvB-GAEZ5B_9M'
#SAMPLE_SPREADSHEET_ID ='1wVxCCt75JyoL8N6wDT2YDNbK9411esNolWUWyHJ9T5g'
SAMPLE_RANGE_NAME = 'Preferences!A2:AA'
#SAMPLE_RANGE_NAME = 'Locker_Responses!A2:I'
#ORDER_SPREADSHEET_ID = '1HBJ4ES21BtVONE_fXGlCRR7i_Jx2ezqluehfeaY1Rr4'
#WRITING_RANGE_RESPONSES = 'Lunch_preorders!Q2:Z'
#WRITING_RANGE = 'Orders!A2:Z'
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

def remove_blanks(vals):
    vals_noblanks = []
    for i in vals:
        print("SDFSDSDFSDF")
        print(i)
        noblank_arr = []
        for j in i:
            #print(j)
            if (j != ""):
                #print(j)
                noblank_arr.append(j)
        vals_noblanks.append(noblank_arr)
    return vals_noblanks

values_noblanks = remove_blanks(values)
#print(values)
