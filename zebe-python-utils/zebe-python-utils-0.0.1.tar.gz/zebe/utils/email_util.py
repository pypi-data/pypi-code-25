# -*- coding: utf-8 -*-
import smtplib
from email.mime.text import MIMEText


# 发送HTML邮件
def send_html_mail(subject, content, host, port, password, sender, receiver):
    msg = MIMEText(content, _subtype='html', _charset='utf-8')
    msg['Subject'] = subject
    msg['From'] = sender
    s = smtplib.SMTP_SSL(host, port)
    s.login(sender, password)
    receiver_emails = []
    if isinstance(receiver, str):
        receiver_emails.append(receiver)
    elif isinstance(receiver, list):
        receiver_emails = receiver
    s.sendmail(sender, receiver_emails, msg.as_string())

