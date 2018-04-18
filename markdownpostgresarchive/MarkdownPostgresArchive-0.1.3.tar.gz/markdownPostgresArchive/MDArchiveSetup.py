import argparse

"""
Dev: Ryan Guard (Guardr2)

Takes user input for database credentials for when the users sets up the required database for pip project
and stores it into a .txt file for reuse later
"""
parser = argparse.ArgumentParser(description='Setup for credentials of database for archive system.'
                                             'Give the:dbname, user, host, port, password of your database'
                                             'Archive system for storing into a database schema must be of '
                                             'CREATE TABLE wiki.page(\n  page_id integer NOT NULL,\n  page_name text NOT NULL,'
                                             '\n  commit_id integer NOT NULL,\n  date_update date NOT NULL,\n  page_file text NOT NULL,'
                                             '\n  CONSTRAINT page_pkey PRIMARY KEY (page_id, commit_id))WITH (  OIDS=FALSE);')
parser.add_argument('dbname',metavar='dbname', type=str, help='Name of Database')
parser.add_argument('user',metavar='user', type=str, help='Name of user connecting to database')
parser.add_argument('password',metavar='password', type=str, help='Name of password of user connecting database')
parser.add_argument('host',metavar='host', type=str, help='Host of the database')
parser.add_argument('port',metavar='port', type=str, help='Port that the database is being run on')
args = parser.parse_args()
with open("DBCredentials.txt", "w") as file:
    file.write(unicode(args.dbname + "\n"))
    file.write(unicode(args.user + "\n"))
    file.write(unicode(args.password + "\n"))
    file.write(unicode(args.host + "\n"))
    file.write(unicode(args.port))
file.close()