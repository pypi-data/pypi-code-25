import sqlite3 as lite
import sys
from ParkingLot import takePlaceFunc
def enterParking(idParking,idCar,con):
    cur = con.cursor()
    cur.execute("Select available,opened From Parking where parkid="+'\''+str(idParking)+'\'')
    data = cur.fetchone()
    if data==None or int(data[0])<=0 or int(data[1])==0:
        return False
    available=int(data[0])
    cur.execute("Select lotid From ParkingLot where free=0 and parkId="+'\''+str(idParking)+'\''+" and carId="+'\''+str(idCar)+'\'')
    data = cur.fetchone()
    if data !=None:
        return False
    cur.execute("Select lotid From ParkingLot where free=1 and parkId="+'\''+str(idParking)+'\'')
    data = cur.fetchone()
    id=str(data[0])
    takePlaceFunc.takePlace(id,idParking,idCar,available,con)
    return True