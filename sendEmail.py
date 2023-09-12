import smtplib
import time
from email.header import Header
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

from randomString import get_random_str
from util import *

if not os.path.exists("./comics"):
    os.mkdir('./comics')
if not os.path.exists("./zips"):
    os.mkdir('./zips')
zip_file("./comics", "./zips")

smtpObj = smtplib.SMTP(os.environ["EMAIL_SERVER_HOST"], os.environ["EMAIL_SERVER_PORT"])
if os.environ["EMAIL_STARTTLS"] == 'true':
    smtpObj.starttls()
email_account = os.environ["EMAIL_ACCOUNT"]
smtpObj.login(email_account, os.environ["EMAIL_AUTH_CODE"])

zips = os.listdir('./zips')
for i in range(len(os.listdir('./zips'))):
    zipFile = zips[i]
    msg = MIMEMultipart()
    msg['From'] = Header(email_account)
    msg['Subject'] = Header('pica comics | ' + generate_random_str(), 'utf-8')
    att = MIMEText(open('./zips/' + zipFile, 'rb').read(), 'base64', 'utf-8')
    att["Content-Type"] = 'application/octet-stream'
    att["Content-Disposition"] = 'attachment; filename="' + zipFile + '"'
    msg.attach(att)
    msg.attach(MIMEText(get_random_str(), 'html', 'utf-8'))
    smtpObj.sendmail(email_account, email_account, msg.as_string())
    # 短时间频繁发邮件容易被邮件服务器检测到, 邮件越多则下封邮件的间隔时间越长
    time.sleep(i * 10)
smtpObj.quit()
