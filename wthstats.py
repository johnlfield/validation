

def PyListoDB(list, dbfile, dbtable):
    # Copy Python list contents into SQLite database table
    # assumes a 3-row header:  column names, SQLite datatypes, and units (this one is ignored)
    dropquery = "DROP TABLE IF EXISTS "+dbtable
    headerquery = "CREATE TABLE "+dbtable+"("
    insertquery = "INSERT INTO "+dbtable+" VALUES("
    for e in range(len(list[0])):           #transform column names & datatypes to string
        headerquery = headerquery+list[0][e]+" "+list[1][e]+", "
    headerquery = headerquery[:-2]+')'
    insertquery = insertquery+e*"?, " + "?)" 
    #simplify python list, deleting initialization row and three header rows
    for i in range(3):
        del list[0]
    #copy python list contents to a DB table
    #SQL table write structure from http://zetcode.com/db/sqlitepythontutorial/
    con = lite.connect(dbfile)              #establish database connection
    with con:
        cur = con.cursor()
        cur.execute(dropquery)
        cur.execute(headerquery)
        cur.executemany(insertquery, list)

def WTHtoDB(csvfile, dbfile, delim):
    # Copy CSV file contents into a SQLite database table
    #arguments- CSV and DB filenames (incl. extensions!), delimiter: c=comma, t=tab
    #copy CSV file contents into a python list
    if delim == "c":
        Lines = csv.reader(open(csvfile, 'rb'))
    elif delim == "t":
        Lines = csv.reader(open(csvfile, 'rb'), delimiter="\t")
    List = [['DOM','Month','Year','DOY','Tmax','Tmin','Precip','Unknown'],
            ['INT','INT','INT','INT','REAL','REAL','REAL','TEXT'],
            ['-','-','-','-','C','C','cm','-']]
    for x in Lines:
        List.append(x)
    #define SQL-format strings to create & populate table
    dbtable = csvfile[:-4]
    os.chdir(dirmain)
    PyListoDB(List, dbfile, dbtable)
    

dirwth = ""
dbfile = "wth.db"

import os
import glob
import csv
import sqlite3 as lite
con = lite.connect(dbfile)
for f in glob.glob(os.path.join(dirwth, '*')):
    if f.endswith(".lis"):
    base = os.path.basename(f)
    csvfile = os.path.splitext(base)[0]
    WTHtoDB(csvfile, dbfile, "t")
    dbtable = csvfile[:-4]
    with con:
        cur = con.cursor()
        cur.execute("ALTER TABLE %s ADD COLUMN GDD FLOAT" % (dbtable))
        cur.execute("UPDATE %s SET GDD=()" % (dbtable))
        cur.execute("CREATE VIEW Temp AS \
                     SELECT AVG(Precip), AVG(GDD) \
                     FROM %s \
                     WHERE Tmax>-90 AND Tmin>-90 AND Precip>-90 \
                     GROUP BY Year" % (dbtable))
        
        labels = cur.fetchall()
        cur.execute("DROP TABLE IF EXISTS Temp")
        cur.execute("DROP TABLE IF EXISTS %s" % (dbtable))
    print filename, precip, GDD