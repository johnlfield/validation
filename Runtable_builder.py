import os
os.chdir('..')

### Copy CSV file contents into a SQLite database table 
def CSVtoDB(csvfile, dbfile, delim):          #arguments- CSV and DB filenames, NO EXTENSION!, delimiter: c=comma, t=tab
    import csv
    import sqlite3 as lite
                                              #copy CSV file contents into a python list
    if delim == "c":
        Lines = csv.reader(open(csvfile, 'rb'))   #import csv file by line
    elif delim == "t":
        Lines = csv.reader(open(csvfile, 'rb'), delimiter="\t")
    List = [[]]                               #initialize a 2D python list to receive CSV contents
    for x in Lines:
        List.append(x)              
                                              #define SQL-format strings to create & populate table
    csv = csvfile[:-4]
    db = dbfile[:-4]
    headerquery = "CREATE TABLE "+csv+"("
    insertquery = "INSERT INTO "+csv+" VALUES("
    for i in range(len(List[1])):             #transform column names & datatypes to a text list
        headerquery = headerquery+List[1][i]+" "+List[2][i]+", "
    headerquery = headerquery[:-2]+')'
    insertquery = insertquery+i*"?, " + "?)" 
                                              #clean up python list
    for i in range(4):
        del List[0]                           #delete initialization row and three header rows
                                              #copy python list contents to a DB table
    dbfile = db+".db"
    con = lite.connect(dbfile)                #establish database connection
    with con:                                 #SQL table write structure from http://zetcode.com/db/sqlitepythontutorial/
        cur = con.cursor()
        cur.execute("DROP TABLE IF EXISTS "+csv)
        cur.execute(headerquery)
        cur.executemany(insertquery, List)


### Process the CSV tables of Sites, Treatments, and Yields
Database = "switchgrass"
CSVtoDB("Sites.csv", Database, "c")
CSVtoDB("Treatments.csv", Database, "c")
CSVtoDB("Yields.csv", Database, "c")
CSVtoDB("FIPS.csv", Database, "c")
CSVtoDB("runfile20130307.dat", Database, "t")

import sqlite3 as lite
con = lite.connect(Database+".db")
with con:
    cur = con.cursor()
    cur.execute("SELECT r.Run, s.mukey, s.NARRx, s.NARRy, s.Lat, s.Long, t.* \
                 FROM Yields y \
                 JOIN Sites s ON y.Site=s.Site \
                 JOIN Treatments t ON y.Treatment=t.Treatment \
                 JOIN FIPS f ON s.ST=f.ST AND s.County=f.County \
                 JOIN runfile20130307 r ON f.FIPS=r.FIPS AND s.NARRx=r.NARRx \
                                        AND s.NARRy=r.NARRy AND s.mukey=r.mukey")
    rows = cur.fetchall()
    print
    print "DayCent runtable: "
    for row in rows:
        print row
    print
