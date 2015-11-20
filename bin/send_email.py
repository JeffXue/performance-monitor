# -*- coding:utf-8 -*-
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText


class EmailHelper:

    host = ''
    user = ''
    password = ''

    def __init__(self, host, user, password):
        self.host = host
        self.user = user
        self.password = password

    def send_email(self, html_msg, subject, receivers):
        msg_root = MIMEMultipart()
        msg_root['From'] = self.user
        msg_root['To'] = ','.join(receivers)
        msg_root["Subject"] = subject

        msg = html_msg
        msg_body = MIMEText(msg, "html", "utf-8")
        msg_root.attach(msg_body)

        smtp = smtplib.SMTP()
        smtp.connect(self.host)
        smtp.login(self.user, self.password)
        smtp.sendmail(self.user, receivers, msg_root.as_string())
        smtp.quit()
