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
from email import encoders

pswd = open('pswd.txt','r')
gmail_user = 'dvhs.makerspace@gmail.com'
gmail_password = pswd.readline().strip()

# If modifying these scopes, delete the file token.json.
SCOPES = ['https://www.googleapis.com/auth/spreadsheets']

# The ID and range of a sample spreadsheet.

SAMPLE_SPREADSHEET_ID ='184zbsKgft5utNUckuXt-p6QqHW1jt2E0f6m_ZOP6dCY'
#SAMPLE_SPREADSHEET_ID ='1wVxCCt75JyoL8N6wDT2YDNbK9411esNolWUWyHJ9T5g'
SAMPLE_RANGE_NAME = 'Locker_Responses!A2:L'
#SAMPLE_RANGE_NAME = 'Locker_Responses!A2:I'
WRITING_RANGE = 'Locker_Responses!A2:L'
UNASSIGNED_LOCKERS_RANGE = 'Unassigned_Lockers!A2:B'
VALUE_INPUT_OPTION = "RAW"

COL_TIMESTAMP=0
COL_FIRST=1
COL_LAST=2
COL_GRADE=3
COL_FLOOR=4
COL_LOCKER_TB=5
COL_PARTNER_FIRST=6
COL_PARTNER_LAST=7
COL_EMAIL_ADDRESS=8
COL_PARTNERS=9
COL_ASSIGNED_LOCKER=10
COL_MATCH_STATUS=11

NUM_STUDENTS = 3500

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
broken_locks = [3063,3217,3234,3357,3092,4122,4220,4527,4659,4665]

unpartnered = {}

def load_partners():
    #store names in a dictionary
    for i in range(len(values)):

        name = values[i][COL_FIRST].lower().strip()+" "+values[i][COL_LAST].lower().strip()
        #print(name)
        num_cols = len(values[i])
        if (num_cols == 9):
            partner = values[i][COL_PARTNER_FIRST].lower().strip() + " "+values[i][COL_PARTNER_LAST].lower().strip()
            #print(partner)
            # If user set partnered with self, un-partner
            if partner == name:
                partner = ''
        else:
            partner = ''

        for k in range(num_cols, 12):
            values[i].append('')

        grade = values[i][3]
        vals = []
        vals.append(partner)
        vals.append(grade)
        vals.append('')
        vals.append('')
        vals.append('')
        data[name] = vals
        if partner == '':
            unpartnered[name] = vals

def set_combined(name, partner):
    partner_msg = name.title()+"/"+partner.title()
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
    print("DATAAAAAAAAAAAAAAAAAAA")
    #print(data)
    for name in data.keys():
        partner = data[name][0]
        grade = data[name][1]

        if (partner != ''):
            if (not partner in data):
                #print(partner)
                unpartner(name)
            #if each person put the other as their partner
            elif (name == data[partner][0] and data[name][1] == data[partner][1]):
                set_combined(name, partner)
                data[name][4] = "MATCH"
                data[partner][4] = "MATCH"
            #A chooses B but B doesn't choose anyone
            elif (data[partner][0] == '' and data[name][0] == partner and data[name][1] == data[partner][1]):
                set_combined(name, partner)
                data[name][4] = "MATCH"
                data[partner][4] = "MATCH"
            else:
                #if A chooses B but B chooses C
                unpartner(name)

def partner_unpartnered():
    unpartnered_names = []

    for i in unpartnered.keys():
        #print(i)
        unpartnered_names.append([i,int(unpartnered[i][1])])
    unpartnered_names = sorted(unpartnered_names, key=itemgetter(1))
    print("UNPARTNERED DICTIONARYYYYY")
    print()
    print_debug(unpartnered_names)

    i = 0
    while (i < len(unpartnered_names)-1):
        name = unpartnered_names[i][0]
        grade = unpartnered_names[i][1]
        next_name = unpartnered_names[i+1][0]
        next_grade = unpartnered_names[i+1][1]
        if (grade == next_grade):
            unpartnered[name][0] = next_name
            i += 2
        else:
            unpartnered[name][0] = name
            next_name = name
            i += 1
        data[name] = unpartnered[name]
        data[name][4] = "ASSIGNED"
        data[next_name][4] = "ASSIGNED"
        set_combined(name, next_name)
        print_debug(data)
        #print()
        print_debug(unpartnered)
        #print()
    if (i == len(unpartnered_names)-1):
        name = unpartnered_names[i][0]
        data[name] = unpartnered[name]
        data[name][4] = "ASSIGNED"
        set_combined(name, name)

def make_lockers(start, end):
    lockers = []
    for i in range(start,end,2):
        if (i not in broken_locks):
            lockers.append(str(i))
    return lockers

def append_lockers(top_bottom, start, end):
    lockers = []
    if (top_bottom == "T"):
        lockers = make_lockers(start+1, end+1)
    else:
        lockers = make_lockers(start, end+1)
    return lockers

def create_lockers():
    #fill locker dictionary
    NUM_LOCKERS = 4
    for i in locker_building.values():
        for j in locker_floor.values():
            locker_T_B[i+j+"T"] = None
            locker_T_B[i+j+"B"] = None
    for i in locker_T_B:
        lockers = []
        #triple_lockers = []
        lockers.append(0)
        if (i[0] == "3"):
            if (i[1] == "1"):
                lockers = append_lockers(i[2],3001,3400)
            elif (i[1] == "2"):
                lockers = append_lockers(i[2],3501,3730)
        elif (i[0] == "2"):
            if (i[1] == "1"):
                lockers = append_lockers(i[2],2001,2358)
            elif (i[1] == "2"):
                lockers = append_lockers(i[2],2501,2716)
        elif (i[0] == "1"):
            if (i[1] == "1"):
                lockers = append_lockers(i[2],1001,1406)
                # triple_lockers = append_lockers(i[2],1,600)
                # for j in triple_lockers:
                #     lockers.append(j)
                # print(i+str(len(lockers)))
            elif (i[1] == "2"):
                lockers = append_lockers(i[2],1501,1730)
                # triple_lockers = append_lockers(i[2],142,570)
                # for k in triple_lockers:
                #     lockers.append(k)
                #print(i+str(len(lockers)))
        elif (i[0] == "4"):
            if (i[1] == "1"):
                lockers = append_lockers(i[2],4001,4335)
            elif (i[1] == "2"):
                lockers = append_lockers(i[2],4501,4678)
        # if (i[0] == "3"):
        #     if (i[1] == "1"):
        #             lockers = append_lockers(i[2],1,3)
        #     else:
        #             lockers = append_lockers(i[2],5,6)
        # elif (i[0] == "2"):
        #     if (i[1] == "1"):
        #         lockers = append_lockers(i[2],7,8)
        #     else:
        #         lockers = append_lockers(i[2],9,10)
        # elif (i[0] == "1"):
        #     if (i[1] == "1"):
        #         lockers = append_lockers(i[2],11,13)
        #     else:
        #         lockers = append_lockers(i[2],15,16)
        # elif (i[0] == "4"):
        #     if (i[1] == "1"):
        #         lockers = append_lockers(i[2],17,18)
        #     else:
        #         lockers = append_lockers(i[2],19,20)
        locker_T_B[i] = lockers


def triple_lockers():
    triple_lower = open("triple_lower.txt","r").read().split("\n")
    triple_upper = open("triple_upper.txt","r").read().split("\n")

    for i in range(int(len(triple_lower)/2)):
        locker_T_B["11B"].append(triple_lower[i])
    for i in range(int(len(triple_lower)/2),len(triple_lower)):
        locker_T_B["11T"].append(triple_lower[i])

    for i in range(int(len(triple_upper)/2)):
        locker_T_B["12B"].append(triple_upper[i])
    for i in range(int(len(triple_upper)/2),len(triple_upper)):
        locker_T_B["12T"].append(triple_upper[i])
    #print(locker_T_B)

def del_zeros():
    for i in locker_T_B:
        del locker_T_B[i][0]

def get_next_locker(locker, TB):
    #print("Len " + locker + TB + ": " + str(len(locker_T_B[locker + TB])))
    if (len(locker_T_B[locker + TB]) != 0):
        print_debug( locker_T_B[locker + TB])
        # + ": " + str(len(locker_T_B[locker + TB])))
        lock_num = locker_T_B[locker + TB][0]
        #print(lock_num)
        del locker_T_B[ locker +TB][0]
        #print(locker_T_B)
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
    if (False):
        print(str)

def load_locker(grade, name, floor, TB):
    #assign locker for one student
    bldg_floor = locker_building[grade] + locker_floor[floor]
    lock_num = get_next_locker(bldg_floor, TB)
    if (lock_num == None):
        print_debug("Ran out: " + bldg_floor + TB)
        TB = get_next_top_bottom(TB)
        #print("Checking: " + bldg_floor + TB)
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
                    print("Ran out of lockers")
                    sys.exit(2)
                    return None
    return lock_num

def assign_locker(grade, name, floor, TB):
    # Partnered student and unassigned locker
    if data[name][3] == '':
        locker = load_locker(grade, name, floor, TB)
        if name in data:
            print_debug( name + ':' + data[name][0])
            data[name][3] = locker
            # Assign partner the same locker
            data[data[name][0]][3] = locker
        elif name in unpartnered:
            unpartnered[name][3] = locker
    #print_debug( locker)
    #print(locker_T_B[locker[0:2]+TB])

def assign_lockers():
    #assign lockers
    for h in range(len(values)):
        grade = values[h][3]
        name = values[h][1].lower().strip()+" "+values[h][2].lower().strip()
        floor = values[h][4]
        TB = values[h][5][0]
        assign_locker(grade, name, floor, TB)
        set_values(h, name)


def remove_invalid_partners():
    for i in unpartnered.keys():
        del data[i]

def set_values(index, name):
    values[index][COL_PARTNERS] = data[name][2]
    values[index][COL_ASSIGNED_LOCKER] = data[name][3]
    values[index][COL_MATCH_STATUS] = data[name][4]

def populate():
    vals = []
    for i in range(NUM_STUDENTS):
        values = []
        values.append("5/12/2019 3:31:5"+str(i))
        if (i > 25):
            values.append(string.ascii_uppercase[i%26]+str(i))
        else:
            values.append(string.ascii_uppercase[i%26])
        if (i > 25):
            values.append(string.ascii_uppercase[i%26]+str(i))
        else:
            values.append(string.ascii_uppercase[i%26])
        integer = random.randint(0,3)
        if (integer == 0):
            values.append("9")
        elif (integer == 1):
            values.append("10")
        elif (integer == 2):
            values.append("11")
        elif (integer == 3):
            values.append("12")
        if (random.randint(0,1) == 0):
            values.append("Top floor")
        else:
            values.append("Bottom floor")
        if (random.randint(0,1) == 0):
            values.append("Top locker")
        else:
            values.append("Bottom locker")
        values.append("")
        values.append("")
        values.append(string.ascii_uppercase[i%26]+str(i)+"@gmail.com")
        vals.append(values)
    return vals

def unassigned_lockers():
    vals = []
    for i in locker_T_B:
        free_locker = []
        if len(locker_T_B[i]) != 0:
            for j in locker_T_B[i]:
                free_locker.append(str(j))
                vals.append(free_locker)
                free_locker = []
    return vals

def createMessage(subject, text=None):
    msg = MIMEMultipart()
    msg['Subject'] = subject
    if text != None:
        msg.attach(MIMEText(text))
    return msg

def print_bldg_totals():
    b1 = 0
    b2 = 0
    b3 = 0
    b4 = 0

    for i in locker_T_B:
        if (i[0] == "1"):
            b1 += len(locker_T_B[i])
        elif (i[0] == "2"):
            b2 += len(locker_T_B[i])
        elif (i[0] == "3"):
            b3 += len(locker_T_B[i])
        elif (i[0] == "4"):
            b4 += len(locker_T_B[i])
        #print(i+": "+str(len(locker_T_B[i])))
        #print()
        #print(locker_T_B[i])
    print()
    print(b1)
    print(b2)
    print(b3)
    print(b4)

def find_dupls():
    num_dupls = 0
    dupls = []
    for i in range(len(values)):
        for j in range(i+1,len(values)):
            fname1 = values[i][1].lower()
            lname1 = values[i][2].lower()
            grade1 = values[i][3]
            email1 = values[i][8]

            fname2 = values[j][1].lower()
            lname2 = values[j][2].lower()
            grade2 = values[j][3]
            email2 = values[j][8]

            if (fname1 == fname2 and lname1 == lname2 and email1 != email2):#and (int(grade1) == 9 or int(grade2) == 9)
                dupl = []
                num_dupls += 1
                #dupl.append()
                print(fname1+" "+lname1+"  Grade: "+grade1+"  Email: "+email1)
                print(fname2+" "+lname2+"  Grade: "+grade2+"  Email: "+email2)
    print(num_dupls)

def send_email():
    try:
        server = smtplib.SMTP_SSL('smtp.gmail.com', 465)
        server.ehlo()
        server.login(gmail_user, gmail_password)
    except Exception as e:
        print(e)

    sent_from = gmail_user
    index_read = int(open("email_index.txt","r").readline().strip())
    for j in range(index_read,len(values)):
        i = values[j]
        to = str(i[8])
        if (len(to) == 0):
            continue
        name = i[1]+" "+i[2]
        subject = "Your Locker for the 2019-2020 School Year"
        #print(data)
        #print(data[name])
        #body = 'Dear '+name+',\n\n'+'Thank you for participating in locker registration. You have been assigned the following locker/partner:\n\n'+'Locker #: '+i[COL_ASSIGNED_LOCKER]+'\n'+'Partner: '+i[9]+'\n\n'+'If you have any questions about the assignment process, please contact Mr. Spain (bspain@srvusd.net).\n\n'+'Thanks,\n'+'San Ramon Makerspace'
        #body = 'Dear '+name+',\n\n'+'Thank you for participating in locker registration. You have been assigned the following locker/partner:\n\n'+'Locker #: '+i[COL_ASSIGNED_LOCKER]+'\n'+'Partner: '+i[9]+'\n\n'+'If you have any questions about the assignment process, please contact Mr. Spain (bspain@srvusd.net).\n\n'+'Thanks,\n'+'San Ramon Makerspace'
        body = 'Dear '+ name + ',\n' + \
            '\n' + \
            'Thank you for participating in locker registration. You have been assigned the following locker/partner:\n' + \
            '\n' + \
            'Locker #: ' + i[COL_ASSIGNED_LOCKER] + \
            '\nPartner: '+ i[9] + \
            '\n' + \
            'If you weren\'t assigned the partner/locker as per your preferences, it was likely because of one of the following:\n' + \
            '\n' + \
            '    * Your partner didn\'t fill out the form\n' + \
            '    * You misspelled your partner\'s name\n' + \
            '    * You filled in your grade in the 2018-2019 school year instead of 2019-2020\n' + \
            '    * You/your partner filled out the form multiple times with different partners\n' + \
            '\n' + \
            'If your situation is different from the ones mentioned above, please contact Mr. Spain (bspain@srvusd.net).\n' + \
            '\n' + \
            'Once all students are assigned, we will begin to appropriately resolve issues. There will be a Google form posted on the school website in the coming week to allow students to register their issues.\n' + \
            '\n' + \
            'Thanks,\n' + \
            'San Ramon Makerspace'

        try:
            msg = createMessage(subject, body)
            server.sendmail(sent_from, to, msg.as_string())
            # x = random.randint(1,100)
            # if (x > 50):
            #     raise Exception('Screwed')
            print('Email sent to: '+to)
        except Exception as e:
            print("ERROR: Failed to send email to: "+to+": "+str(e))
            index = open("email_index.txt","w")
            index.write(str(j))
            index.close()
            break
            #print(e)
            # server.close()
            # server = smtplib.SMTP_SSL('smtp.gmail.com', 465)
            # server.ehlo()
            # server.login(gmail_user, gmail_password)

    server.close()

create_lockers()
triple_lockers()
#del_zeros()
print_bldg_totals()
length = 0
for i in locker_T_B:
    length += len(locker_T_B[i])
    #for j in i:
    #    if j in broken_locks:
            #print(j)
#print(broken_locks)
#print(length)
#print(data)
if not values:
    print('No data found.')
else:
   load_partners()
   # validate_partners()
   # #print(data)
   # partner_unpartnered()
   # # #
   # #
   # #find_dupls()
   # remove_invalid_partners()
   # assign_lockers()
   # #print(data)
   # free_lockers = unassigned_lockers()
   #print(data)
   send_email()
#lockers = populate()


#
# body = {'values': values}
# result = service.spreadsheets().values().update(
# spreadsheetId=SAMPLE_SPREADSHEET_ID, range=WRITING_RANGE,
# valueInputOption=VALUE_INPUT_OPTION, body=body).execute()
#
# body = {'values': free_lockers}
# result = service.spreadsheets().values().update(
# spreadsheetId=SAMPLE_SPREADSHEET_ID, range=UNASSIGNED_LOCKERS_RANGE,
# valueInputOption=VALUE_INPUT_OPTION, body=body).execute()
