import sqlite3 as lite
import sys
import os

abspath = os.path.abspath(__file__)     #get absolute path where script is located
dname = os.path.dirname(abspath)        #get associated directory only
os.chdir(dname)                         #set that as working directory


### DATA IMPORT METHOD 1
# con = lite.connect('test.db')
# with con:
#     cur = con.cursor()
#     cur.execute("DROP TABLE IF EXISTS Cars")    
#     cur.execute("CREATE TABLE Cars(Id INT, Name TEXT, Price INT)")
#     cur.execute("INSERT INTO Cars VALUES(1,'Audi',52642)")
#     cur.execute("INSERT INTO Cars VALUES(2,'Mercedes',57127)")
#     cur.execute("INSERT INTO Cars VALUES(3,'Skoda',9000)")
#     cur.execute("INSERT INTO Cars VALUES(4,'Volvo',29000)")
#     cur.execute("INSERT INTO Cars VALUES(5,'Bentley',350000)")
#     cur.execute("INSERT INTO Cars VALUES(6,'Citroen',21000)")
#     cur.execute("INSERT INTO Cars VALUES(7,'Hummer',41400)")
#     cur.execute("INSERT INTO Cars VALUES(8,'Volkswagen',21600)")


### DATA IMPORT METHOD 2
cars = (
    (1, 'Audi', 52642),
    (2, 'Mercedes', 57127),
    (3, 'Skoda', 9000),
    (4, 'Volvo', 29000),
    (5, 'Bentley', 350000),
    (6, 'Hummer', 41400),
    (7, 'Volkswagen', 21600)
)

con = lite.connect('test.db')
with con:
    cur = con.cursor()    
    cur.execute("DROP TABLE IF EXISTS Cars")
    cur.execute("CREATE TABLE Cars(Id INT, Name TEXT, Price INT)")
    cur.executemany("INSERT INTO Cars VALUES(?, ?, ?)", cars)

    cur.execute("SELECT *, Price*.001 FROM Cars WHERE Price > 50000 AND Name IN ('Audi', 'Mercedes') ORDER BY Price DESC")
    rows = cur.fetchall()
    for row in rows:
        print row