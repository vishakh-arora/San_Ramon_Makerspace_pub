import smtplib
import csv
import email
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email.mime.text import MIMEText
from email.mime.image import MIMEImage
from email import encoders

OUTPUT_PATH = "./assignments_raw.csv"

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

def generate_email(school_id, grade, lname, fname, email, partner_lname, partner_fname, partner_email, locker):
    to = email
    name = fname[0].upper()+fname[1:]
    subject = "Locker Assignment for the 2021-22 School Year"

    add_on = 'and partner ' if grade == '9' else ''
    partner = '<u><b>Partner:</b></u> {} {} ({})<br>'.format(partner_fname[0].upper()+partner_fname[1:], partner_lname[0].upper()+partner_lname[1:], email) if (grade == '9') else ''
    school = 'DVHS' if (school_id == '0') else 'CHS'
    vp = 'Jennifer Lee at <a href="mailto: jlee2@srvusd.net">jlee2@srvusd.net</a>' if (school == 'DVHS') else 'Jeffrey Osborn at <a href="mailto: josborn1@srvusd.net">josborn1@srvusd.net</a>'
    lock = 'Your lock will already be on your locker by the time school starts. A {} administrator will contact you with the combination.'.format(school) if (grade == '9') else 'Please remember to bring the lock that was loaned to you by {} when you return to campus; if it has been lost, it can be replaced through the Webstore for a $10 fee. Any non-{} issued lock will be removed from lockers.'.format(school, school)

    htmlbody = '<html><body>Dear {},<br>'.format(name) + \
        '<br>' + \
        'Thank you for using the new website to record your locker preferences. Please find your assigned locker {}below.<br>'.format(add_on) + \
        '<br><u><b>Locker:</b></u> {}'.format(locker) + \
        '<br>{}'.format(partner) + \
        '<br>If you have been assigned a locker that doesn\'t work for you due to your or your partner\'s physical/medical constraints, please have one of you contact {}.'.format(vp) + \
' {}<br><br>Thanks,'.format(lock) + \
        '<br>San Ramon Makerspace</body></html>'
#    print("TEXTTT: "+htmlbody)
    try:
        mail(to, subject, text=None, html=htmlbody)

    except Exception as e:
        print("ERROR: Failed to send email to: "+to+": "+str(e))

def read_output():
    assignments = list(csv.reader(open(OUTPUT_PATH)))

    for a in assignments:
        for i in range(len(a)):
            a[i] = a[i].strip()
        generate_email(a[SCHOOL_ID], a[GRADE], a[S_LNAME], a[S_FNAME], a[S_EMAIL], a[P_LNAME], a[P_FNAME], a[P_EMAIL], a[LOCKER])

if (__name__ == "__main__"):
    read_output()
