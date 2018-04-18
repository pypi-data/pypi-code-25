from io import open

from markdownArchiveStandalone.ArchivePage import ArchivePage
from markdownArchiveStandalone.ArchiveDatabaseConnection import ArchiveDatabaseConnection



"""
Dev: Liam Tiemon (tiemonl1)

Takes the contents of a markdown file and restores it from the database.
Then uses ArchivePage to store the pulled page as a new page.
"""
class RestorePage:
    """
    Constructor gets the name of the file with the extensions and the url. It then reads what is in the given file.
    """
    def __init__(self, name, url):
        self.fileName = name
        self.path = url
        self.cursor = ArchiveDatabaseConnection().conn.cursor()

    """
    Selects the given page from the database and writes a new file with the contents from the pulled page.
    It then stores the page using ArchivePage's store function.
    """
    def restore(self,commitID):
        self.cursor.execute("SELECT page_file FROM wiki.page WHERE page_name='"+self.fileName+"' AND commit_id="+commitID.__str__())

        rows = self.cursor.fetchall()
        with open(self.path, "w",encoding='utf-8') as file:
            for row in rows:
                str = row[0].__str__()
                file.write(unicode(str))
        file.close()
        name = self.fileName
        arc = ArchivePage(name, self.path)
        arc.store()

