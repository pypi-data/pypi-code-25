import sqlite3 as lite
import sys
def openParking(idParking,con):
    cur = con.cursor()
    cur.execute("Select parkid From Parking where parkid="+'\''+str(idParking)+'\'')
    data = cur.fetchone()
    if data==None :
        return False
    cur.execute("UPDATE Parking Set opened=1 where parkId="+'\''+str(idParking)+'\'')
    return True