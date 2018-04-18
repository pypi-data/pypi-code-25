from ArchiveDatabaseConnection import ArchiveDatabaseConnection
"""
Dev: Elizabeth Gieske with adaptations for console input from Ryan Guard (Guardr2)

Takes user inputted page name and displays the history of it that is stored in the database.
"""

"""
Holds data for displaying history data
"""
class HistoryPage():

    def __init__(self, page_name, page_commit, timestamp, user):
        self.page_name = page_name
        self.commit = page_commit
        self.timestamp = timestamp
        self.user = user

"""
Displays available commits that have been made with the user that submitted them and its date.
"""
def displayHistoryConsole(page_name):
    cursor = ArchiveDatabaseConnection().conn.cursor()
    cursor.execute("Select DISTINCT(page_name) from wiki.page ORDER BY page_name")
    page_names = cursor.fetchall()
    cursor.execute("Select commit_id, page_name, date_update, user_last_update from wiki.page ORDER BY commit_id DESC")
    inner = cursor.fetchall()

    page_dict = {}
    for pg in page_names:
        page_dict[pg[0]] = []

    for pg in inner:
        h_pg = HistoryPage(pg[1],pg[0],pg[2],pg[3])
        page_dict[pg[1]].append(h_pg)

    for pg in page_dict[page_name]:
        print "Commit#: " + pg.commit.__str__() + " User:" + pg.user.__str__() + " Date: " + pg.timestamp.__str__()


"""
Dev: Ryan Guard(Guardr2)

Prints out a specified page commit's contents for user to see
"""
def displayHistoryContents(page_name, commit_id):
    cursor = ArchiveDatabaseConnection().conn.cursor()
    cursor.execute("SELECT page_file FROM wiki.page WHERE page_name='"+page_name+"' AND commit_id=" + commit_id.__str__())
    page_content = cursor.fetchall()
    for pg in page_content:
        print "Name: " + page_name + "\n" + pg[0]