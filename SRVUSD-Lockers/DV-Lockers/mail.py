import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email.mime.text import MIMEText
from email import encoders

gmail_user = 'dvhs.makerspace@gmail.com'
gmail_password = 'M@ker$pace'

sent_from = gmail_user
to = 'vishakh.arora29@gmail.com'
subject = 'Python Mail Test'
body = 'mail test; this is the body\nThanks,\nSan Ramon Makerspace'

email_text = """\
From: %s
To: %s
Subject: %s

%s
""" % (sent_from, to, subject, body)

def createMessage(subject, text=None):
    msg = MIMEMultipart()
    msg['Subject'] = subject
    if text != None:
        msg.attach(MIMEText(text))
    return msg

try:
    server = smtplib.SMTP_SSL('smtp.gmail.com', 465)
    server.ehlo()
    server.login(gmail_user, gmail_password)
    msg = createMessage(subject, body)
    server.sendmail(sent_from, to, msg.as_string())
    server.close()

    print('Email sent!')
except Exception as e:
    print(e)
