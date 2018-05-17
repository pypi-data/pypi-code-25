from email.mime.text import MIMEText
from smtplib import SMTP_SSL


class EmailSender:
    def __init__(self, email_conf):
        self.smtp_server = email_conf['smtp_server']
        self.port = email_conf['port']
        self.user = email_conf['user']
        self.password = email_conf['password']
        self.sender = email_conf['sender']
        self.default_receiver = email_conf['receiver']

    def send(self, subject, text, receiver=None):
        if receiver is None:
            receiver = self.default_receiver
        msg = MIMEText(text, "plain", "utf-8")
        msg['From'] = self.sender
        msg['To'] = receiver
        msg['Subject'] = subject
        smtp = SMTP_SSL()
        smtp.connect('smtp.yandex.ru', 465)
        smtp.login(self.user, self.password)
        smtp.sendmail(self.sender, receiver, msg.as_string())
        smtp.quit()
