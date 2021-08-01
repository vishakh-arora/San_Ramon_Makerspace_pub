from __future__ import print_function
#from PIL import Image
from googleapiclient.discovery import build
from httplib2 import Http
from oauth2client import file, client, tools
from google.oauth2 import service_account
from operator import itemgetter
import googleapiclient.discovery
import smtplib
import dkim
import email
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email.mime.text import MIMEText
from email.mime.image import MIMEImage
from email import encoders

def mail(to, subject, text=None, html=None, attach=None):
   msg = MIMEMultipart()
   from_user = "<do-not-reply@lockermatch.com>"
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

   # if (attach != None):
   #     fp = open(attach, 'rb')
   #     msgImage = MIMEImage(fp.read())
   #     fp.close()

       # msgImage.add_header('Content-ID', '<image1>')
       # msg.attach(msgImage)
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

def generate_email():
    #i = vals
#    to = "kumar.shubham5504@gmail.com"
#    to = "spamlifeeee@gmail.com"
#    to = "vishakh.arora29@gmail.com"
    to = "test-7817ef@test.mailgenius.com"
    #name = i[COL_NAME]

    subject = "Lockermatch Testing"

     # The embedded image doesn't show up in gmail so use inline attachment
     # '<br>\n<img src="data:image/png;base64,{0}" alt="">'.format(data_uri) + \
    htmlbody = 'lockermatch test'
    print("TEXTTT: "+htmlbody)
#    textbody=strip_html( htmlbody)

    try:
        mail(to, subject, text=htmlbody, html=None)

    except Exception as e:
        print("ERROR: Failed to send email to: "+to+": "+str(e))

generate_email()
