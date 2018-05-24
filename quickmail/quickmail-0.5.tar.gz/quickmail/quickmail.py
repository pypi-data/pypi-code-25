#!/usr/bin/env python
import os
import sys
import vmtools
import smtplib
from email.mime.text import MIMEText
from os.path import basename
from email.mime.multipart import MIMEMultipart
from email.mime.application import MIMEApplication


vm_root_path = vmtools.vm_root_grabber()
sys.path.append(vm_root_path)
import pkgutil
local_settings_present = pkgutil.find_loader('local_settings')
if local_settings_present:
    from local_settings import *

def senderror(subject_text, body_text, username, password, smtp_ssl_host, smtp_ssl_port, recipients, attachment_files_path_list=[]):
    """Take subject_text, body_text, username, password, recipients, and optionally attachment_files_path, send email
    
    :type subject_text: string
    :param subject_text: the subject for the email
    :type body_text: string
    :param body_text: the body for the email
    :type username: string
    :param username: the gmail username
    :type password: string
    :param password: the gmail password
    :type  smtp_ssl_host: string
    :param smtp_ssl_host: the ssl enabled smtp host
    :type  smtp_ssl_port: int
    :param smtp_ssl_port: the ssl port to use
    :type recipients: list
    :param recpients: list of recipients
    :type attachment_files_path_list: list
    :param attachment_files_path_list: list of strings that are absolute file paths to the files to attach
    """

    # construct message
    msg = MIMEMultipart()
    msg['Subject'] = subject_text
    msg['From'] = username
    msg['To'] = ', '.join(recipients)
    msg.attach(MIMEText(body_text))


    # attach any attachments
    for attachment_file_path in attachment_files_path_list or []:
        with open(attachment_file_path, "rb") as fil:
            part = MIMEApplication(fil.read(), Name=basename(attachment_file_path))
        part['Content-Disposition'] = 'attachment; filename="%s"' % basename(attachment_file_path)
        msg.attach(part)

    # connect and send email
    server = smtplib.SMTP_SSL(smtp_ssl_host, smtp_ssl_port)
    server.login(username, password)
    server.sendmail(username, recipients, msg.as_string())
    server.quit()

def senderror_simple(subject_text, body_text, attachment_files_path_list=[]):
    """Take subject_text and body_text and send with mail account
    NB: this function requires thatf you store in local_settings.py at the root of the python virtual machine the following (you can avoid specifying the arguments: username, password, recipients):
    import os
    #mail settings
    MAIL_CONFIG_DICT = {
        SMTP_SSL_HOST': 'yourdomain.com',
        SMTP_SSL_PORT': <port>,
        MAIL_USER='you@yourdomain.com'
        MAIL_PASS='changeme'
        MAIL_RECIPIENTS=['friend1@theirdomain.com', 'friend2@theirdoman.com']
        }
    
    :type subject_text: string
    :param subject_text: the subject for the email
    :type body_text: string
    :param body_text: the body for the email
    :type attachment_files_path_list: list
    :param attachment_files_path_list: list of strings that are absolute file paths to the files to attach
    """
    senderror(subject_text=subject_text, body_text=body_text, username=MAIL_CONFIG_DICT['MAIL_USER'], password=MAIL_CONFIG_DICT['MAIL_PASS'], smtp_ssl_host=MAIL_CONFIG_DICT['SMTP_SSL_HOST'], smtp_ssl_port=MAIL_CONFIG_DICT['SMTP_SSL_PORT'], recipients=MAIL_CONFIG_DICT['MAIL_RECIPIENTS'], attachment_files_path_list=attachment_files_path_list)
