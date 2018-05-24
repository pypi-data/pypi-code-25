import sqlite3 as lite
import sys
def connection():
    con = lite.connect('ParkManagement.db')
    with con:
        cur = con.cursor()
        cur.execute("CREATE TABLE ParkingLot(parkId TEXT,lotId TEXT, carId TEXT, free INT)")
        cur.execute("CREATE TABLE Parking(parkId TEXT, available INT, opened INT)")
    return con