

def PyListoDB(list, dbfile, dbtable):
    # Copy Python list contents into SQLite database table
    # assumes a 3-row header:  column names, SQLite datatypes, and units (this one is ignored)
    import sqlite3 as lite
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
    os.chdir(dirmain)
    con = lite.connect(dbfile)              #establish database connection
    with con:
        cur = con.cursor()
        cur.execute(dropquery)
        cur.execute(headerquery)
        cur.executemany(insertquery, list)
        
 
def CSVtoDB(csvfile, dbfile, delim):
    # Copy CSV file contents into a SQLite database table
    #arguments- CSV and DB filenames (incl. extensions!), delimiter: c=comma, t=tab
    import csv
    os.chdir(dirrun)
    #copy CSV file contents into a python list
    if delim == "c":
        Lines = csv.reader(open(csvfile, 'rb'))
    elif delim == "t":
        Lines = csv.reader(open(csvfile, 'rb'), delimiter="\t")
    List = [[]]
    for x in Lines:
        List.append(x)
    #define SQL-format strings to create & populate table
    dbtable = csvfile[:-4]
    del List[0]
    os.chdir(dirmain)
    PyListoDB(List, dbfile, dbtable)
    

def multiplot(xname, yname, x, y, divisions, divisor, dbtable, dbfile):
    # x, y & divisor are SQLite column names, divisions an integer
    os.chdir(dirmain)
    import matplotlib.pyplot as plt
    plt.plot([0,30], [0,30], color="black")
    if divisions==0:
        con = lite.connect(dbfile)
        with con:
            cur = con.cursor()
            cur.execute("SELECT DISTINCT %s FROM %s" % (divisor, dbtable))
            cat = cur.fetchall()
            print "Unique categories: ", cat
        e=0
        for i in cat:
            val = str(cat[e])[2:][:-2]
            print "index= ", e
            print "value= ", val
            lab = val[:1]+divisor+" "+val[1:]
            exec('print "WHERE %s=%s"' % (divisor,val))
            exec('query = "WHERE %s=%s"' % (divisor,val))
            extractseries(x, y, dbtable, dbfile, query, lab)
            e += 1
        plt.legend()
    elif divisions==1:
        query = ""
        lab = "all"
        extractseries(x, y, dbtable, dbfile, query, lab)
    else:
        con = lite.connect(dbfile)
        with con:
            cur = con.cursor()
            cur.execute("SELECT %s FROM %s" % (divisor, dbtable))
            cat = cur.fetchall()
            minval = min(cat) 
            minval = float(str(minval)[1:][:-2])
            maxval = max(cat)
            maxval = float(str(maxval)[1:][:-2])
            inter = round((maxval-minval)/divisions, 3)
            print "Min/Max/interval values: ", minval, "/", maxval, "/", inter
        for i in range(divisions):
            low = round(minval+inter*i, 3)
            high = round(minval+inter*(i+1), 3)
            print "Range: ", low, "-", high
            lab = "'"+str(low)+"<"+str(divisor)+"<"+str(high)+"'"
            exec('print "WHERE %s BETWEEN %s AND %s"' % (divisor,low,high))
            exec('query = "WHERE %s BETWEEN %s AND %s"' % (divisor,low,high))
            extractseries(x, y, dbtable, dbfile, query, lab)
        plt.legend()
    plt.title('%s vs. %s' % (yname,xname))
    plt.xlabel('%s' % (xname))
    plt.ylabel('%s' % (yname))
    plt.savefig("detail.png")
    plt.close()
          
        
def extractseries(x, y, dbtable, dbfile, query, lab):
    import sqlite3 as lite
    import matplotlib.pyplot as plt
    con = lite.connect(dbfile)
    with con:
        cur = con.cursor()
        cur.execute("PRAGMA table_info(%s)" % (dbtable))
        labels = cur.fetchall()
        cur.execute("SELECT * FROM %s %s" % (dbtable,query))
        values = cur.fetchall()
        i = -1
        for row in labels:
            name = row[1].split(":")[0]
            if name=="AVG(Yield)":
                name = "AVG_yield"
            elif name=="AVG(DDC_yield)":
                name = "AVG_DDC_yield"
            exec('%s=[]' % (name))
            i += 1
            for line in values:
                exec('%s.append(list(line)[i])' % (name))
            exec('print "%s = ", %s' % (name,name))
    print "Plotting results... "+y+" versus "+x
    print
    exec("plt.plot(%s, %s,'o', label=%s)" % (x,y,lab))








### File and path definitions ###########################################################
import os
abspath = os.path.abspath(__file__)       #get absolute path where script is located
dname = os.path.dirname(abspath)          #associated directory only
os.chdir(dname)
os.chdir('..')
os.chdir('..')                            #navigate TWO directories higher
dirmain = os.getcwd()
dirres = dirmain+"/results/2013-09-06,11.41"
dirrun = dirmain+"/runtable/001"
dbfile = "switch.db"
DDC_yield_column = "DDC_yield"
viewname1 = "Combo"
viewname2 = "Filtered"


### import, label, concatenate & copy .lis files to SQLite database #####################
os.chdir(dirres)
import glob
import numpy as np
i = 1
for f in glob.glob(os.path.join(dirres, '*')):
    if f.endswith(".lis"):                       #for each .lis file in the archive 
        g = open(f)
        lines = g.readlines()
        labels = lines[1].split()
        base = os.path.basename(f)
        filename = os.path.splitext(base)[0]     #split off the filename       
        id = filename.split("_")
        npdata = np.genfromtxt(f, skip_header=3) #import .lis data as numpy array
        listdata = npdata.tolist()               #convert numpy array to Python list
        for row in listdata:
            year = row[0]
            year = int(year)-1
            row[0] = year
            row.insert(0, id[2])                 #add treatment ID to each entry
            row.insert(0, id[1])
            row.insert(0, id[0])
        del listdata[0]                          #delete the first row (DDC repeat)
        if i == 1:
            DDClis = listdata                    #initialize with first .lis file
        else:
            DDClis = DDClis+listdata             #concatenate files
        i += 1
header = ['Study', 'Site', 'Treatment'] + labels
columns = len(header)
header2 = ['TEXT', 'TEXT','TEXT']
for i in range(columns-3):
    header2.append('FLOAT')
header3 = ['']
for i in range(columns-1):
    header3.append('')
DDClis.insert(0, header3)
DDClis.insert(0, header2)
DDClis.insert(0, header)
print "Copying DayCent results to SQLite database table..."
print
os.chdir(dirmain)
PyListoDB(DDClis, dbfile, 'Modeled')


### convert crmvst to real units, and add as a column ###################################
c_conc = 0.45                          #define biomass carbon concentration 
import sqlite3 as lite
con = lite.connect(dbfile)
with con:
    cur = con.cursor()
    cur.execute("ALTER TABLE Modeled ADD COLUMN %s FLOAT" % (DDC_yield_column))
    cur.execute("UPDATE Modeled SET %s=((crmvst/%s)*.01)" % (DDC_yield_column,c_conc))


### add Site, Treatment, and expanded measured Yield data to database ###################
import csv
CSVtoDB("Sites.csv", dbfile, "c")
CSVtoDB("Treatments.csv", dbfile, "c")
os.chdir(dirrun)
annmeas = [['Study','Site','Treatment','Year','Yield'], \
           ['TEXT','TEXT','TEXT','INT','FLOAT'], ['','','','','']]
annyields = csv.reader(open('Yields.csv', 'rb'))        #import yields.csv
temp = [[]]         #copy results into a temporary Python table for easier manipulation
for row in annyields:
    temp.append(row)
del temp[0]
i=0
for row in temp:
    if i>2:
        for j in range(len(temp[0])-5):
            year = temp[0][j+5]
            year = year[1:]
            entry = [temp[i][0], temp[i][1], temp[i][2], year, temp[i][j+5]]
            annmeas.append(entry)
    i += 1
PyListoDB(annmeas, dbfile, 'Measured')


### define database views that JOIN, FILTER take treatment AVERAGES of the results ######
with con:
    cur = con.cursor()
    cur.execute("DROP TABLE IF EXISTS FINAL")
    cur.execute("DROP VIEW IF EXISTS %s" % (viewname1))
    cur.execute("DROP VIEW IF EXISTS %s" % (viewname2))
    cur.execute("CREATE VIEW %s AS \
                 SELECT a.*, m.*, s.*, t.* FROM Measured a \
                 JOIN Modeled m ON a.Study=m.Study AND a.Site=m.Site \
                      AND a.Treatment=m.Treatment AND a.Year=m.time \
                 JOIN Sites s ON s.Study=a.Study AND s.Site=a.Site \
                 JOIN Treatments t ON t.Study=a.Study AND t.Treatment=a.Treatment \
                 WHERE a.Yield>0 AND m.time<2010" % (viewname1))
    cur.execute("CREATE VIEW %s AS \
                 SELECT *, AVG(Yield), AVG(DDC_yield) FROM %s \
                 WHERE SGN1_rate>0 AND Avg_precip>0 \
                 GROUP BY Study, Site, Treatment" % (viewname2,viewname1))
    c = csv.writer(open("detail.csv", "wb"))
    cur.execute("PRAGMA table_info(%s)" % (viewname2))
    labels = cur.fetchall()
    header = []
    for row in labels:
        header.append(row[1])
    c.writerow(header)
    cur.execute("SELECT * FROM %s" % (viewname2))
    rows = cur.fetchall()
    for row in rows:
        c.writerow(row)
    
    
### plot results ########################################################################
# Arguements: 'xlabel', 'ylable', x 'SQL column', y 'SQL column', #divisions, divisor 'SQL column'
multiplot("Measured", "Modeled", "AVG_yield", "AVG_DDC_yield", 4, "Avg_GDD", \
          viewname2, dbfile)