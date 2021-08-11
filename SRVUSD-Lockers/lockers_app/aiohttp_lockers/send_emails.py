import smtplib
import csv
import pandas as pd
import numpy as np
import email
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email.mime.text import MIMEText
from email.mime.image import MIMEImage
from email import encoders

OUTPUT_PATH = "dh_assignment.csv"
#OUTPUT_PATH = "assignments_raw.csv"
CHS_LOCKERS = "test_sheets/CHSLockerTest.xlsx"
DVHS_LOCKERS = "test_sheets/DVHSLockerCombos.xlsx"
SUCCESSES = 0

SCHOOL_ID = 0
GRADE = 1
S_LNAME = 2
S_FNAME = 3
S_EMAIL = 4
P_LNAME = 5
P_FNAME = 6
P_EMAIL = 7
LOCKER = 8

def mail(to, subject, text=None, html=None, attach=None):
   msg = MIMEMultipart()
   from_user = "<do-not-reply@lockermatch.com>"
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

   # if (attach != None):
   #     fp = open(attach, 'rb')
   #     msgImage = MIMEImage(fp.read())
   #     fp.close()

       # msgImage.add_header('Content-ID', '<image1>')
       # msg.attach(msgImage)
           # part = MIMEBase('application', 'octet-stream')
           # part.set_payload(open(attach, 'rb').read())
           # encoders.encode_base64(part)
           # part.add_header('Content-Disposition', 'attachment; filename="{}"' % os.path.basename(attach))
           # msg.attach(part)

   mailServer = smtplib.SMTP("localhost", 587)
   mailServer.ehlo()
   mailServer.starttls()
   #mailServer.ehlo()
#   mailServer.login(gmail_user, gmail_password)
   mailServer.sendmail(from_user, to, msg.as_string())
   # Should be mailServer.quit(), but that crashes...
   mailServer.close()

def generate_email(a, locker_info, sheet_columns):
    global SUCCESSES

    to = a[S_EMAIL]
    name = a[S_FNAME][0].upper()+a[S_FNAME][1:]
    subject = "Locker Assignment for the 2021-22 School Year"

    partnered = True if (a[P_EMAIL] != a[S_EMAIL]) else False
    add_on = 'partner and ' if partnered else ''
    locker = '{}<br>'.format(a[LOCKER]) if partnered else a[LOCKER]
    partner = '<u><b>Partner:</b></u> {} {} ({})<br>'.format(a[P_FNAME][0].upper()+a[P_FNAME][1:], a[P_LNAME][0].upper()+a[P_LNAME][1:], a[P_EMAIL]) if (partnered) else ''
    location = ''
    for i in range(len(locker_info[1:])):
        location += '<br><u><b>{}:</b></u> {}'.format(sheet_columns[i+2], locker_info[i+1])
    school = 'DVHS' if (a[SCHOOL_ID] == '0') else 'CHS'
    combination = '<br><u><b>Combination:</b></u> {}'.format(locker_info[0]) if locker_info[0] != '10,20,30' else '<br>A {} administrator will contact you with the combination.'.format(school) if (a[GRADE] == '9') else ''
    vp = 'Jennifer Lee at <a href="mailto: jlee2@srvusd.net">jlee2@srvusd.net</a>' if (school == 'DVHS') else 'Jeffrey Osborn at <a href="mailto: josborn1@srvusd.net">josborn1@srvusd.net</a>'
    # lock = 'Your lock will already be on your locker by the time school starts.' if (a[GRADE] == '9') else 'Please remember to bring the lock that was loaned to you by {} when you return to campus; if it has been lost, it can be replaced through the Webstore for a $10 fee. Any non-{} issued lock will be removed from lockers.'.format(school, school)
    lock = 'Only freshmen will be provided DVHS locks this year. All 10th, 11th, and 12th graders must bring or purchase their own locks from elsewhere (If you have a school-issued lock from the past, you may continue using it).' if (school == 'DVHS') else ''
    constraint = [' or your partner\'s', ' have one of you'] if partnered else ['','']

    htmlbody = '<html><body>Dear {},<br>'.format(name) + \
        '<br>' + \
        'Thank you for using the new website to record your locker preferences. Please find your assigned {}locker below.<br><br>'.format(add_on) + \
        '{}'.format(partner) + \
        '<u><b>Locker:</b></u> {}'.format(locker) + \
        '{}'.format(location) + \
        '{}<br>'.format(combination) + \
        '<br>{}'.format(lock) + \
        ' If you have been assigned a locker that doesn\'t work for you due to your{} physical/medical constraints, please{} contact {}.'.format(constraint[0], constraint[1], vp) + \
        '<br><br>Thanks,' + \
        '<br>San Ramon Makerspace</body></html>'
#    print("TEXTTT: "+htmlbody)
    try:
        mail(to, subject, text=None, html=htmlbody)
        print('Successfully sent email to {}'.format(to))
        SUCCESSES += 1
    except Exception as e:
        print("ERROR: Failed to send email to: "+to+": "+str(e))

def read_sheet(sheet_file):
    df = pd.read_excel(sheet_file, engine='openpyxl')
    sheet_columns = list(df.columns)
    sheet_data = df.to_numpy()
    locker_json = dict(zip(sheet_data[:,0],sheet_data[:,1:]))
    return (locker_json, sheet_columns)

def read_output():
    assignments = list(csv.reader(open(OUTPUT_PATH)))
    dvhs_lockers, dvhs_columns = read_sheet(DVHS_LOCKERS)
    chs_lockers, chs_columns = read_sheet(CHS_LOCKERS)

    for a in assignments:
        for i in range(len(a)):
            a[i] = a[i].strip()

        if a[SCHOOL_ID] == '0':
            generate_email(a, dvhs_lockers.get(int(a[LOCKER])), dvhs_columns)
        elif a[SCHOOL_ID] == '1':
            generate_email(a, chs_lockers.get(int(a[LOCKER])), chs_columns)
    print('\nSuccessfully sent email to {}/{} students'.format(SUCCESSES, len(assignments)))

if (__name__ == "__main__"):
    read_output()
