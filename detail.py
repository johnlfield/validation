# def convert():

def multiplot(view, x, y, divisions, divisor):
# x, y & divisor are SQLite column names, divisions an integer
    if divisions==1:
        query = ""
#         convert()
        import matplotlib.pyplot as plt    
        exec('xvar=%s' % (x))
        exec('yvar=%s' % (x))
        yvar = '%s' % (x)
        plt.plot(xvar, yvar, 'o')
        plt.title('%s vs. %s' % (y,x))
        plt.xlabel('%s' % (x))
        plt.ylabel('%s' % (y))
        plt.savefig("test.png")
        plt.close()
        
def CSVextractall(dbtable, dbfile, query):
    import sqlite3 as lite
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
            exec('%s=[]' % (name))
            i += 1
            for line in values:
                exec('%s.append(list(line)[i])' % (name))
#             exec('print "%s = ", %s' % (name,name))




import os
dbfile = "switch.db"
viewname1 = "Combo"
viewname2 = "Filtered"
abspath = os.path.abspath(__file__)     #get absolute path where script is located
dname = os.path.dirname(abspath)        #associated directory only
os.chdir(dname)
os.chdir('..')
os.chdir('..')                          #navigate TWO directories higher
dirmain = os.getcwd()
dirres = dirmain+"/results/2013-09-06,11.41"
dirrun = dirmain+"/runtable/001"

import sqlite3 as lite
con = lite.connect(dbfile)
with con:
    cur = con.cursor()
    cur.execute("DROP VIEW IF EXISTS %s" % (viewname1))
    cur.execute("DROP VIEW IF EXISTS %s" % (viewname2))
    cur.execute("CREATE VIEW %s AS \
                 SELECT a.*, m.*, s.*, t.* FROM Ann_meas a \
                 JOIN Modeled m ON a.Study=m.Study AND a.Site=m.Site \
                      AND a.Treatment=m.Treatment AND a.Year=m.time \
                 JOIN Sites s ON s.Study=a.Study AND s.Site=a.Site \
                 JOIN Treatments t ON t.Study=a.Study AND t.Treatment=a.Treatment \
                 WHERE a.Yield>0 AND m.time<2010" % (viewname1))
    cur.execute("CREATE VIEW %s AS \
                 SELECT * FROM %s \
                 WHERE somtc>1" % (viewname2,viewname1))
CSVextractall(viewname1, dbfile, "")                #just to initialize all variables
