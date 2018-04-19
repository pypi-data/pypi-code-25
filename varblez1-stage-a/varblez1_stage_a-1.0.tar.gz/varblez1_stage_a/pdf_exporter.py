import argparse
import markdown
import pdfkit
import smtplib
from email.mime.application import MIMEApplication
from email.mime.multipart import MIMEMultipart

"""
This can be called on as a python library by the individual functions 
or in command line, where it will only perform the mail_pdf function.

    in command line its called by:
        export_pdf.py input.md address1, address2.. address# [--s subject]   
"""

def return_pdf(page):
    """
    converts markdown into html and then into pdf
    :param page: the markdown file to be converted
    :return: a pdf formated file
    """
    html_text = markdown.markdown(page.read(), output_format='html4')

    path_wkthmltopdf = r'C:\Python27\wkhtmltopdf\bin\wkhtmltopdf.exe'
    config = pdfkit.configuration(wkhtmltopdf=path_wkthmltopdf)
    options = {'--header-html': r'C:\Users\zv\PycharmProjects\Riki\wiki\web\templates\header.html'}
    pdf = pdfkit.from_string(html_text, False, options=options, configuration=config)
    print "test 2"
    return pdf

def return_pdf_directory(dir):
    """
    an intermidiary function that lets return_pdf be called with a directory location instead of a file directory
    :param dir: a string containing the directory of a .md file
    :return: returns output of return_pdf
    """
    fp = open(dir)
    return return_pdf(fp)

def mail_pdf(page, address, subject='Requested Page'):
    """
    creates a pdf form a markdown file by calling return_pdf_directory and then emails it to target addresses

    :param page: a string containing the path to a .md file
    :param address: an array of strings containing the email addresses to be sent to
    :param subject: a string containing the subject line of the email
    :return: returns nothing
    """
    pdf = return_pdf_directory(page)
    fromMy = 'wikibest@yahoo.com'
    to = address
    msg = MIMEMultipart()
    msg['Subject'] = subject
    msg['From'] = 'wikibest@yahoo.com'
    msg['To'] = ", ".join(to)
    msg.preamble = subject
    file = MIMEApplication(pdf, _subtype = 'pdf')
    file.add_header('content-disposition', 'attachment', filename='file.pdf')
    msg.attach(file)

    username = str('wikibest@yahoo.com')
    password = str('Software440')
    try:
        server = smtplib.SMTP("smtp.mail.yahoo.com", 587)
        server.starttls()
        server.login(username, password)
        server.sendmail(fromMy, to, msg.as_string())
        server.quit()
        print 'ok the email has sent '
    except:
        print 'can\'t send the Email'



def parse():
    """
    parses arguments from command line and calls mail_pdf with apropriet arguments
    :return:  returns nothing
    """
    parser = argparse.ArgumentParser()
    parser.add_argument("page", help="file to be converted")
    parser.add_argument("adrress", nargs='+', help="email address to send file to")
    parser.add_argument("--s",help="Optional Subject line for email")
    args = parser.parse_args()

    mail_pdf(args.page,args.adrress, args.s if args.s else "Requested Page")

if __name__ == '__main__':
    parse()
