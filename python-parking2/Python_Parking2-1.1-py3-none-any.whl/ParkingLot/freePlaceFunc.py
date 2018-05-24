import sqlite3 as lite
import sys
def freePlace(id,idParking,available,con):
    cur = con.cursor()
    cur.execute("UPDATE ParkingLot Set free=1 where lotId="+'\''+id+'\'')
    available=available+1
    cur.execute("UPDATE Parking Set available="+str(available)+" where parkId="+'\''+str(idParking)+'\'')
    return True