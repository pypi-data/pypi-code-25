import imaplib
import logging
import time


def __login(email, password):
    """
    The account must allow POP and IMAP and also allow "less apps"
        see here: https://support.google.com/accounts/answer/6010255?hl=en
        If link is down, go to "Account" -> "Sign-in & Security" -> "Apps with account access"

    :param email:
    :type email: str
    :param password:
    :type password: str
    :return:
    :rtype: imaplib.IMAP4_SSL
    """
    mail = imaplib.IMAP4_SSL('imap.gmail.com')
    mail.login(email, password)
    mail.select("inbox")  # connect to inbox.
    return mail


def __logout(mail):
    """
    :param mail:
    :type mail: imaplib.IMAP4_SSL
    """
    mail.close()
    mail.logout()


def get_email_body_by_criteria(email, password, criteria):
    """

    Example criteria string: '(BODY "123 Main St" FROM "members@dollarshaveclub.cm")'
    
    See README for all criteria params.

    Criteria parameters: multi-word arguments (e.g. SUBJECT "To Whom") must be in quotes.

    :param email: email address
    :type email: str
    :param password: email password
    :type password: str
    :param criteria: string, delimited by spaces. Results will match all criteria parameters
    :type criteria: str
    :return: body of email
    :rtype: bytes
    """
    mail = __login(email, password)
    mail_list = __get_email_id_list_by_criteria(email, password, criteria)
    mail_list.reverse()  # order is now newest to oldest. [0] is newest
    num = mail_list[0]

    typ, data = mail.fetch(num, '(UID BODY[TEXT])')
    if data is None:
        time.sleep(1)
        print("Email body was none. Instant retry")
        return get_email_body_by_criteria(email, password, criteria)
    body = data[0][1]  # assigns body text

    __logout(mail)
    return body


def __get_email_id_list_by_criteria(email, password, criteria, retries=10):
    """


    :param email:
    :type email: str
    :param password:
    :type password: str
    :return email_ids:
    :rtype: list
    """
    mail = __login(email, password)
    typ, data = mail.search(None, criteria)
    email_ids = data[0].split()
    if not email_ids and retries > 0:
        logging.info("No emails. Please retry")
        print("No emails. Please retry")
        time.sleep(15)
        __get_email_id_list_by_criteria(email, password, criteria, retries=retries - 1)
    elif not email_ids and retries <= 0:
        logging.critical("No confirmation email found after 10 tries")
        raise Exception
    elif email_ids:
        logging.debug(f"Email ID list: {email_ids}")
        __logout(mail)
        return email_ids
