import sqlite3 as lite
import sys
def showParkings(con):
    cur = con.cursor()
    cur.execute("Select * From Parking")
    data = cur.fetchall()
    result=''
    for t in data:
        count=0
        temp=''
        for k in t:
            if count==0:
                temp="Parking o id: "+str(k)
            elif count==1:
                temp=temp+", dostepne miejsca: "+str(k)
            else:
                if int(k)==1:
                    temp=temp+", otwarty"+'\n'
                else:
                    temp=temp+", zamkniety"+'\n'
            count=count+1
        result=result+temp
    return str(result)