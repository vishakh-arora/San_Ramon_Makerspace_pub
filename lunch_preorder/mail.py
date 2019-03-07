import os
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email.mime.text import MIMEText
from email import encoders
# And imghdr to find the types of our images
import imghdr

fin = open("mail_credentials","r")
mail_credentials = fin.read().split("\n")


def mail(to, subject, text=None, attach=None):
   msg = MIMEMultipart()
   msg['From'] = mail_credentials[0]
   msg['To'] = to
#','.split(to)
   msg['Subject'] = subject
   if text != None:
   	msg.attach(MIMEText(text))
   if attach != None:
	   part = MIMEBase('application', 'octet-stream')
	   part.set_payload(open(attach, 'rb').read())
	   encoders.encode_base64(part)
	   part.add_header('Content-Disposition', 'attachment; filename="%s"' % os.path.basename(attach))
	   msg.attach(part)

   mailServer = smtplib.SMTP("smtp.gmail.com", 587)
   mailServer.ehlo()
   mailServer.starttls()
   mailServer.ehlo()
   mailServer.login(mail_credentials[0], mail_credentials[1])
   mailServer.sendmail(mail_credentials, to, msg.as_string())
   # Should be mailServer.quit(), but that crashes...
   mailServer.close()

