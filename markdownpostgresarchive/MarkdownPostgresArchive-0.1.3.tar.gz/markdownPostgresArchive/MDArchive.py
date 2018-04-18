import argparse

from markdownArchiveStandalone.ArchivePage import ArchivePage
from markdownArchiveStandalone.DisplayHistory import displayHistoryConsole, displayHistoryContents
from markdownArchiveStandalone.RestorePage import RestorePage

"""
Dev: Ryan Guard (Guardr2)

Takes user input for either storing markdown files into a database for archiving purposes.
They either use --store name path or --restore name path commit_id

"""
parser = argparse.ArgumentParser(description='YOU RUN MDArchiveSetup.py FIRST TO SETUP DATABASE CREDENTIALS'
                                             'Archive system for storing into a database schema must be of '
                                             'CREATE TABLE wiki.page(\n  page_id integer NOT NULL,\n  page_name text NOT NULL,'
                                             '\n  commit_id integer NOT NULL,\n  date_update date NOT NULL,\n  page_file text NOT NULL,'
                                             '\n  CONSTRAINT page_pkey PRIMARY KEY (page_id, commit_id))WITH (  OIDS=FALSE);'
                                             '\n  With database active, this can store versions of files or restore to'
                                             '\n  previous versions already stored in the database')
parser.add_argument('--store', help='Specifies to store the given file', action='store_true')
parser.add_argument('name',metavar='name', type=str, help='Name of File to archive/retrieve')
parser.add_argument('path',metavar='path', nargs="?", type=str, help='Complete file path to file')
parser.add_argument('--restore', type=int, help='stores the commit number and acts as a flag to restore to that commit must use name and path positional with this optional')
parser.add_argument('--show', help='Flags for command to show previous versions of specified file name currently stored in the database', action='store_true')
parser.add_argument('--showContent', type=int, help='stores the commit number and acts as a flag to show that commit')

args = parser.parse_args()
if args.store:
    if args.path:
        try:
            ArchivePage(args.name,args.path).store()
            print "Stored the markdown file into database"
        except:
            print "Error: please check your inputted filename and path"
    else:
        print "Store requires a name, and path to execute"
elif args.restore:
    if args.path:
        try:
            RestorePage(args.name,args.path).restore(args.restore)
            print "restored"
        except:
            print "Error: Failed to restore please check your inputs"
    else:
        print "Restore requires a name, path, and commit_id to execute"
elif args.show:
    try:
        displayHistoryConsole(args.name)
    except:
       print "Error: Failed to restore please check your file name given"
elif args.showContent:
    try:
        displayHistoryContents(args.name,args.showContent)
    except:
        print "Error: Failed to showContent please check your inputs"
else:
    print "please supply -h, --store, --retrieve, --show, or --showContent in your command"