import smtplib
from email.message import EmailMessage
from pyautomailer.importer import Importer
from pyautomailer.body import Body

class PyAutoMailer:

    # Email client information
    ec_host = '' # host
    ec_port = 25 # port
    ec_user = '' # username
    ec_pwd = '' # password

    m_subject = ''

    def set(self, m_from, m_subject, source_file, body_file):
        self.m_from = m_from
        self.m_subject = m_subject
        self.source_file = source_file
        self.body_file = body_file
        self.importer = Importer(self.source_file)

    def set_emailclient(self, host, port, user, pwd):
        self.ec_host = host
        if port != None:
            self.ec_port = port
        self.ec_user = user
        self.ec_pwd = pwd
        self.ec = smtplib.SMTP(self.ec_host, self.ec_port)
        self.ec.login(self.ec_user, self.ec_pwd)

    def emailclient_quit(self):
        self.ec.quit()

    def run_service(self, test_mode):
        for i in range(1,len(self.importer.records_fields)):
            b = Body(self.body_file, self.importer.records_fields, i)
            msg = self.create_message(
                self.m_subject,
                self.m_from, # Sender.
                self.importer.records_fields[i][0], # First fields is email.
                b.html)
            if not test_mode:
                self.ec.send_message(msg)

    def create_message(self, m_subject, m_from, m_to, m_body):
        m = EmailMessage()
        m.set_content(m_body)
        m.add_alternative(m_body, subtype='html')
        m['Subject'] = m_subject
        m['From'] = m_from
        m['To'] = m_to
        return m
