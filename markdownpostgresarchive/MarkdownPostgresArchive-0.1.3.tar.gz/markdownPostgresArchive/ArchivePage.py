from io import open

from markdownArchiveStandalone.ArchiveDatabaseConnection import ArchiveDatabaseConnection

"""
Dev: Ryan Guard (Guardr2)

Takes the contents of a markdown file and storing it in the database.
Inserts the page as a version to possibly be restored to.
"""
class ArchivePage:
    """
    Reads the contents of a given markdown file at the url (local file path to markdown). Parses file information
    as well as the currently logged in user from the session for storage.
    """
    def __init__(self, name, url):
        self.fileName = name
        self.path = url
        self.file = open(self.path, "r")
        self.contents = ""
        for line in self.file.readlines():
            self.contents +=  line.__str__()
        self.contentBytes = str.encode(self.contents)
        self.cursor = ArchiveDatabaseConnection().conn.cursor()
        self.user_id = "StandaloneConsoleApp"


    """
    Checks to see if the page (markdown file) has already been stored. if so it inserts it with a matching page_id, name
    and incremented commit_id with the current contents of page and user information.
    If the page is new, it is stored with a fresh page_id, and its information with the commit_id starting at 1 for english
    enumeration.
    """
    def store(self):
        self.cursor.execute("Select page_name from wiki.page where page_name = '" + self.fileName + "'")
        if len(self.cursor.fetchall()) > 0:
            self.cursor.execute("INSERT INTO wiki.page(page_id,page_name,commit_id,date_update, page_file,user_last_update)"
                                " VALUES((SELECT DISTINCT page_id from wiki.page where page_name = '" + self.fileName + "'),"
                                " '" + self.fileName + "', (SELECT (count(commit_id) + 1) from wiki.page "
                                "where page_name = '" + self.fileName + "') "
                                ", current_date,  '" + self.contents + "','" + self.user_id + "')")
            self.cursor.execute("COMMIT")

        else:
            self.cursor.execute("INSERT INTO wiki.page(page_id,page_name,commit_id,date_update, page_file, user_last_update)"
                                "VALUES((SELECT COUNT(DISTINCT page_id) + 1 from wiki.page), '" + self.fileName + "',1, CURRENT_DATE,'"
                                + self.contents + "','" + self.user_id + "')")
            self.cursor.execute("COMMIT")