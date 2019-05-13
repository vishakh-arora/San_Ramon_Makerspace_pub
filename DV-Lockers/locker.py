# Work with Python 3.6
from __future__ import print_function
from PIL import Image
from googleapiclient.discovery import build
from httplib2 import Http
from oauth2client import file, client, tools
from google.oauth2 import service_account
import googleapiclient.discovery

#<<<<<<< HEAD:discord_bot.py
# If modifying these scopes, delete the file token.json.
SCOPES = ['https://www.googleapis.com/auth/spreadsheets']

# The ID and range of a sample spreadsheet.
SAMPLE_SPREADSHEET_ID = '1drq5UmjxV_9FHMBQf-tDtqlJ6ftOHRI0LEAbF33c9S4'
SAMPLE_RANGE_NAME = 'Locker_Responses!A2:H'
WRITING_RANGE = 'Locker_Responses!A2:J'
VALUE_INPUT_OPTION = "RAW"

SERVICE_ACCOUNT_FILE = 'service.json'
#=======


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
vals = []

locker_building = {
    "9":"4",
    "10":"3",
    "11":"2",
    "12":"1"
}

locker_floor = {
    "Top floor":"2",
    "Bottom floor":"1"
}

locker_T_B = {}

data = {}

unpartnered = {}

def load_partners():
    #store spreadsheet values in a dictionary
    for i in range(len(values)):
        print(values[i])
        name = values[i][1].lower()+" "+values[i][2].lower()
        num_cols = len(values[i])
        if  num_cols == 8:
            partner = values[i][6].lower() + " "+values[i][7].lower()
            # If user set partnered with self, un-partner
            if partner == name:
                partner = ''
        else:
            partner = ''

        for k in range(num_cols, 10):
            values[i].append('')

        grade = values[i][3]
        vals = []
        vals.append(partner)
        vals.append(grade)
        vals.append('')
        vals.append('')
        data[name] = vals
        if partner == '':
            unpartnered[name] = vals

def set_combined(name, partner):
    partner_msg = name+"/"+partner
    #store names in the dictionary
    data[name][2] = partner_msg
    data[partner][2] = partner_msg
    data[name][0] = partner
    data[partner][0] = name
    if name in unpartnered:
        del unpartnered[name]
    if partner in unpartnered:
        del unpartnered[partner]

def unpartner(name):
    unpartnered[name] = data[name]

def validate_partners():
    for name in data.keys():
        partner = data[name][0]
        grade = data[name][1]

        if (partner != ''):
            if (not partner in data):
                unpartner(name)
            #if each person put the other as their partner
            elif (name == data[partner][0] and data[name][1] == data[partner][1]):
                set_combined(name, partner)
            #A chooses B but B doesn't choose anyone
            elif (data[partner][0] == '' and data[name][0] == partner and data[name][1] == data[partner][1]):
                set_combined(name, partner)
            else:
                #if A chooses B but B chooses C
                unpartner(name)

def partner_unpartnered():
    unpartnered_names = list(unpartnered.keys())
    for i in range(0,len(unpartnered_names)-1,2):
        name = unpartnered_names[i]
        next_name = unpartnered_names[i+1]
        unpartnered[name][0] = next_name
        data[name] = unpartnered[name]
        set_combined(name, next_name)

def create_lockers():
    #fill locker dictionary
    NUM_LOCKERS = 3
    for i in locker_building.values():
        for j in locker_floor.values():
            locker_T_B[i+j+"T"] = None
            locker_T_B[i+j+"B"] = None
    for i in locker_T_B.keys():
        lockers = []
        for j in range(NUM_LOCKERS):
            if i[2] == "B":
                lockers.append("0"+str(j))
            else:
                lockers.append("0"+str(j+5))
        locker_T_B[i] = lockers

def get_next_locker(locker, TB):
    print_debug("Len " + locker + TB + ": " + str(len(locker_T_B[locker + TB])))
    if (len(locker_T_B[locker + TB]) != 0):
        print_debug( locker_T_B[locker + TB])
        # + ": " + str(len(locker_T_B[locker + TB])))
        lock_num = locker_T_B[locker + TB][0]
        print_debug(lock_num)
        del locker_T_B[ locker +TB][0]
        return lock_num
    return None

def get_next_floor(floor):
    if (floor == "Top floor"):
        return "Bottom floor"
    elif (floor == "Bottom floor"):
        return "Top floor"

def get_next_top_bottom(TB):
    if (TB == "T"):
        return 'B'
    return 'T'


def print_debug(str):
    if (True):
        print(str)

def load_locker(grade, name, floor, TB):
    #assign locker for one student
    bldg_floor = locker_building[grade] + locker_floor[floor]
    lock_num = get_next_locker(bldg_floor, TB)
    if (lock_num == None):
        print_debug("Ran out: " + bldg_floor + TB)
        TB = get_next_top_bottom(TB)
        print_debug("Checking: " + bldg_floor + TB)
        lock_num = get_next_locker(bldg_floor, TB)
        if (lock_num == None):
            print_debug("Changing floor: " + bldg_floor + TB)
            floor = get_next_floor(floor)
            bldg_floor = locker_building[grade] + locker_floor[floor]
            lock_num = get_next_locker(bldg_floor, TB)
            if (lock_num == None):
                TB = get_next_top_bottom(TB)
                lock_num = get_next_locker(bldg_floor, TB)
                if (lock_num == None):
                    print_debug("Ran out of lockers")
                    return None
    return bldg_floor + lock_num

def assign_locker(grade, name, floor, TB):
    locker = load_locker(grade, name, floor, TB)
    if name in data and data[name][3] == '':
        print_debug( name + ':' + data[name][0])
        data[name][3] = locker
        data[data[name][0]][3] = locker
    elif name in unpartnered:
        unpartnered[name][3] = locker
    print_debug( locker)
    #print(locker_T_B[locker[0:2]+TB])

def assign_lockers():
    #assign lockers
    for h in range(len(values)):
        grade = values[h][3]
        name = values[h][1].lower()+" "+values[h][2].lower()
        floor = values[h][4]
        TB = values[h][5][0]
        assign_locker(grade, name, floor, TB)
        set_values(h, name)


def remove_invalid_partners():
    for i in unpartnered.keys():
        del data[i]

def set_values(index, name):
    values[index][8] = data[name][2]
    values[index][9] = data[name][3]

create_lockers()
print(locker_T_B)
if not values:
    print('No data found.')
else:
    load_partners()

    validate_partners()
    partner_unpartnered()
    #print(values)

    remove_invalid_partners()
    print(data)
    assign_lockers()
    print()
    print(data)
    print()
    print(unpartnered)


body = {'values': values}
result = service.spreadsheets().values().update(
spreadsheetId=SAMPLE_SPREADSHEET_ID, range=WRITING_RANGE,
valueInputOption=VALUE_INPUT_OPTION, body=body).execute()
                #print('{0} cells appended.'.format(result.get('updates').get('updatedCells')))
