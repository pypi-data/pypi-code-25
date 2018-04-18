import os
import psycopg2

"""
Dev: Ryan Guard (Guardr2)

Object that is responsible for connecting to our AWS postgresql database. This module was made with the intention
of reuse throughout the project as necessary.

Takes database credentials from DBCredentials.txt for establishing connection
These credentials are established when user runs MDArchiveSetup.py
"""
class ArchiveDatabaseConnection():
    def __init__(self):
        self.lines = list(open(os.path.dirname(os.path.abspath(__file__)) +"/DBCredentials.txt","r"))
        dbname = self.lines[0].strip()
        user = self.lines[1].strip()
        host = self.lines[3].strip()
        port = self.lines[4].strip()
        password = self.lines[2].strip()
        try:
            self.conn = psycopg2.connect("dbname='" + dbname + "' "
                                 "user='" + user + "'"
                                 "host='" + host + "'"
                                 "port='" + port + "'"
                                 "password='" + password + "'")
            print "connection success"
        except:
            print "connection failure"