import sqlite3 as lite
import sys
def takePlace(id,idParking,idCar,available,con):
    cur = con.cursor()
    cur.execute("UPDATE ParkingLot Set carId="+'\''+str(idCar)+'\''+",free=0 where lotId="+'\''+id+'\'')
    available=available-1
    cur.execute("UPDATE Parking Set available="+str(available)+" where parkId="+'\''+str(idParking)+'\'')
    return True