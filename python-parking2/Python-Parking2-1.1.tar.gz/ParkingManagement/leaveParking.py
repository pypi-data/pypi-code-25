import sqlite3 as lite
import sys
from ParkingLot import freePlaceFunc
def leaveParking(idParking,idCar,con):
    cur = con.cursor()
    cur.execute("Select available From Parking where parkid="+'\''+str(idParking)+'\'')
    data = cur.fetchone()
    if data==None :
        return False
    available=int(data[0])
    cur.execute("Select lotid From ParkingLot where free=0 and parkId="+'\''+str(idParking)+'\''+" and carId="+'\''+str(idCar)+'\'')
    data = cur.fetchone()
    if data ==None:
        return False
    id=str(data[0])
    freePlaceFunc.freePlace(id,idParking,available,con)
    return True