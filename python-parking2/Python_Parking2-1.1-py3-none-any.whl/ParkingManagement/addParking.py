import sqlite3 as lite
import sys
def addParkings(id,number,con):
    cur = con.cursor()
    cur.execute("INSERT INTO Parking VALUES("+'\''+id+'\''+","+str(number)+",1)")
    for i in range(int(number)):
         cur.execute("INSERT INTO ParkingLot VALUES("+'\''+id+'\''+","+'\''+id+str(i)+'\''+",'0',1)")