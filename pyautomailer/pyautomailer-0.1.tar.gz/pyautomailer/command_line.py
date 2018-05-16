import argparse
import sys
from pyautomailer import PyAutoMailer

def main():
    parser = parse_args(sys.argv[1:])
    am = PyAutoMailer()
    am.set(parser.sender, parser.subject, parser.source_file, parser.body_file)
    am.set_emailclient(parser.host, parser.port, parser.user, parser.pwd)
    am.run_service(parser.test)
    am.emailclient_quit()

def parse_args(args):
    parser = argparse.ArgumentParser('A fully customizable automatic email client service.')
    parser.add_argument('host', metavar='HOST', type=str,
                        help='Email client host.')
    parser.add_argument('-p', '--port', type=int,
                        help='Email client host port.')
    parser.add_argument('user', metavar='USER', type=str,
                        help='Email client host username.')
    parser.add_argument('pwd', metavar='PWD', type=str,
                        help='Email client host password.')
    parser.add_argument('sender', metavar='SENDER', type=str,
                        help='Email client sender.')
    parser.add_argument('source_file', metavar='SOURCE_FILE', type=str,
                        help='Source .csv file containing emails and dynamics fields.')
    parser.add_argument('-s', '--subject', type=str,
                        help='Subject of email.')
    parser.add_argument('body_file', metavar='BODY_FILE', type=str,
                        help='HTML body file.')
    parser.add_argument('-t', '--test', action='store_true',
                        help='Run sending test without sending real mails.')
    
    return parser.parse_args(args)
