
# Copy Python list contents into SQLite database table
# assumes a 3-row header:  column names, SQLite datatypes, and units (this one is ignored)
def PyListoDB(list, dbfile, dbtable):
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
    con = lite.connect(dbfile)              #establish database connection
    with con:
        cur = con.cursor()
        cur.execute(dropquery)
        cur.execute(headerquery)
        cur.executemany(insertquery, list)
        
# Copy CSV file contents into a SQLite database table 
def CSVtoDB(csvfile, dbfile, delim):
#arguments- CSV and DB filenames (incl. extensions!), delimiter: c=comma, t=tab
    import csv
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
    PyListoDB(List, dbfile, dbtable)

#plot measured versus modeled results, broken down by ecotype
def MMplot (meas, mod, measU, modU, measL, modL, measQ, modQ, filename):
    import matplotlib.pyplot as plt
    from scipy import stats
    plt.plot([0,30], [0,30])       
    plt.plot(measL, modL, 'go', label='Lowland')
    plt.plot(measU, modU, 'ro', label='Upland')
    plt.plot(measQ, modQ, 'bo', label='unspecified')
    plt.legend()
    plt.title(filename[:-4])
    plt.xlabel('Measured switchgrass yield (dry Mg/ha)')
    plt.ylabel('Modeled switchgrass yield (dry Mg/ha)')
    slope, intercept, r_value, p_value, std_err = stats.linregress(meas,mod)
    plt.text(2, 26, 'Combined regression statistics: \nPearson correlation coefficient=%s \
                     \nP-value=%s' % (round(r_value,3),round(p_value,4)))
    plt.savefig(filename)
    plt.close()

#plot error regressed versus X
def EvXplot (error, regressor, label, filename):
    import matplotlib.pyplot as plt
    from scipy import stats      
    plt.plot(regressor, error, 'go')
    plt.title(filename[:-4])
    plt.xlabel(label)
    plt.ylabel('Error')
    slope, intercept, r_value, p_value, std_err = stats.linregress(regressor,error)
    miny=min(error)
    maxy=max(error)
    minx=min(regressor)
    maxx=max(regressor)
    plt.text(.03*(maxx-minx)+minx, .95*(maxy-miny)+miny, 'Combined regression statistics: \
             \nPearson correlation coefficient=%s \nP-value=%s' \
             % (round(r_value,3),round(p_value,4)))
    plt.plot([minx,maxx], [intercept+slope*minx,intercept+slope*maxx])
    plt.savefig(filename)
    plt.close()
    

### HEADER
print
print
print "This script facilitates a DayCent yield validation analysis sequence, including"
print "  * generating a DayCent model runtable based on 'Sites.csv', 'Treatments.csv',"
print "    and 'Yields.csv'"
print "  * performing an automated analysis of an associated DayCent results archive"
print "    against measured values in 'Yields.csv', including the calculation of fit"
print "    statistics, gnereation of plots, and tracking of metadata"
print
print "It requires the following directory structure:"
print "    Main directory: 'switchgrass.db'"
print "    Subdirectory 'results': repository for archived analysis results"
print "    Subdirectory 'runtable': contains a series of archive folders containing the"
print "        required 'Sites.csv', 'Treatments.csv', and 'Yields.csv', as well as the"
print "        supporting 'FIPS.csv' and a .dat file matching the appropriate CFARM .dsa"
print "        binary archive on the network"
print "    Subdirectory 'scripts'/subdirectory 'validation': this script 'validation00X.py'"
print
print "Analysis results will automatically be archived along with a log file to help"
print "track metadata and the provinence of the analysis."
print


### RUNTABLE BULDER
import os
Database = "switch.db"
abspath = os.path.abspath(__file__)     #get absolute path where script is located
dname = os.path.dirname(abspath)        #associated directory only
os.chdir(dname)
os.chdir('..')
os.chdir('..')                          #navigate TWO directories higher
dirmain = os.getcwd()
print "If you would like to generate a new DayCent runtable, please enter the RUNTABLE"
print "archive number to use:"
runarch = raw_input()
if runarch != "":
    #specification of all relevant directory paths
    import glob
    import shutil
    dirrun = dirmain+"/runtable/"+runarch
    print "Please type a descriptive filename (no spaces or file extension) for this runtable:"
    title = raw_input()
    outfile = title+"_"+runarch+".csv"
    print
    
    #if the file described doesn't already exist, generate it 
    #otherwise, return an error and move on
    if not os.path.exists(dirrun+"/"+outfile):   
        #move necessary .csv/.dat files to main working directory
        #copy all runtable archive components to SQLite database
        os.chdir(dirrun)
        for f in glob.glob(os.path.join(dirrun, '*')):
            if f.endswith(".csv") or f.endswith(".dat"):  
                shutil.copy(f, dirmain) 
        os.chdir(dirmain)         
        print "Copying runtable CSV files to SQLite database tables..."
        print
        CSVtoDB("Sites.csv", Database, "c")
        CSVtoDB("Treatments.csv", Database, "c")
        CSVtoDB("Yields.csv", Database, "c")
        CSVtoDB("FIPS.csv", Database, "c")
        CSVtoDB("runfile20130307.dat", Database, "t")
        for f in glob.glob(os.path.join(dirmain, '*')):
            if f.endswith(".csv") or f.endswith(".dat"):  
                os.remove(f) 
            
        #create a runtable based on each entry in 'Yields.csv', using joins to bring in site 
        #data, FIPS codes, and CFARM equilibrium archive run numbers
        print "Joining tables to generate DayCent runtable..."
        print
        import csv
        import sqlite3 as lite
        con = lite.connect(Database)
        with con:
            cur = con.cursor()
            cur.execute("SELECT r.Run, s.mukey, s.NARRx, s.NARRy, s.Lat, s.Long, t.*, s.Site, s.ST \
                        FROM Yields y \
                        JOIN Sites s ON y.Site=s.Site \
                        JOIN Treatments t ON y.Treatment=t.Treatment AND y.Study=t.Study \
                        JOIN FIPS f ON s.ST=f.ST AND s.County=f.County \
                        JOIN runfile20130307 r ON f.FIPS=r.FIPS AND s.NARRx=r.NARRx \
                                                AND s.NARRy=r.NARRy AND s.mukey=r.mukey")
            rows = cur.fetchall()
            c = csv.writer(open(outfile, "wb"))
            print "Runtable being saved as '"+outfile+":"
            for row in rows:
                print row
                c.writerow(row)
            shutil.move(outfile, dirrun)
            print
            print
    else:
        print "** A file of that description already exists in the specified runtable archive;"
        print "       runtable generation terminated **"
        print
        print


### RESULTS ANALYSIS
print "If you would like to analyze a DayCent results archive against a dataset of field"
print "trial yield results, please enter the RUNTABLE archive number where the appropriate"
print "'Yield.csv' file can be found:"
runarch = raw_input()
if runarch != "":
    print "And the RESULTS archive number you wish to compare:"
    resarch = raw_input()
    dirres = dirmain+"/results/"+resarch
    dirrun = dirmain+"/runtable/"+runarch
    print
    script = os.path.basename(__file__)
    print "Analysis code version:  ", script
    print

    # import, label, concatenate & copy .lis files to SQLite database
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
        header2.append('INT')
    header3 = ['']
    for i in range(columns-1):
        header3.append('')    
    DDClis.insert(0, header3)
    DDClis.insert(0, header2)
    DDClis.insert(0, header)
    print "Copying DayCent results to SQLite database table..."
    print
    os.chdir(dirmain)
    PyListoDB(DDClis, Database, 'Modeled')

    #copy average yields from 'Yields.cvs' to SQLite database
    os.chdir(dirrun)
    import csv
    avgyields = csv.reader(open('Yields.csv', 'rb'))        #import yields.csv
    avgmeas = [[]]
    for row in avgyields:                 #convert each row of csv file values to a list element
        entry = [row[0], row[1], row[2], row[3]]
        avgmeas.append(entry)
    del avgmeas[0]
    print "Copying measured yield values to SQLite database table..."
    print
    os.chdir(dirmain)
    PyListoDB(avgmeas, Database, 'Avg_meas')
    
    #expand and copy annual yields from 'Yields.cvs' to SQLite database
    os.chdir(dirrun)
    annmeas = [['Study','Site','Treatment','Year','Yield'], \
               ['TEXT','TEXT','TEXT','INT','REAL'], ['','','','','']]
    annyields = csv.reader(open('Yields.csv', 'rb'))        #import yields.csv
    #copy results into a temporary Python table for easier manipulation
    temp = [[]]
    for row in annyields:
        temp.append(row)
    del temp[0]
    i=0
    for row in temp:
        if i>2:
            j = 0
            for col in range(24):
                entry = [temp[i][0], temp[i][1], temp[i][2], temp[0][j+4], temp[i][j+4]]
                annmeas.append(entry)
                j += 1
        i += 1
    os.chdir(dirmain)
    PyListoDB(annmeas, Database, 'Ann_meas')

    #query all annual measured yields, modeled yields, and supporting metadata
    c_conc = 0.45                          #define biomass carbon concentration
    logfile = "Log.txt"
    import csv
    import sqlite3 as lite
    con = lite.connect(Database)
    with con:
        cur = con.cursor()
        cur.execute("SELECT a.Study, a.Site, a.Treatment, t.Ecotype, s.Lat, s.Long, \
                     s.Avg_precip, s. Avg_GDD, s.sand, s.NI_LCC, t.SGN1_rate, t.Harv_DOY, \
                     a.Year, a.Yield, (m.crmvst/.45)*0.01, \
                     ((((m.crmvst/%s)*0.01)-a.Yield)/a.Yield) \
                     FROM Ann_meas a \
                     JOIN Modeled m ON a.Study=m.Study AND a.Site=m.Site AND \
                          a.Treatment=m.Treatment AND a.Year=m.time \
                     JOIN Sites s ON s.Study=a.Study AND s.Site=a.Site \
                     JOIN Treatments t ON t.Study=a.Study AND t.Treatment=a.Treatment \
                     WHERE a.Yield>0" % (c_conc))
        rows = cur.fetchall()
        c = csv.writer(open(logfile, "wb"))
        
###update so that all .csv tables are re-loaded to the DB along with Yield.csv
## add metadata print out here!!!!
        print "Results log being saved as '"+logfile+"'..."
        print
        Eco=[]
        Lat=[]
        Long=[]
        Precip=[]
        GDD=[]
        Sand=[]
        LCC=[]
        Nrate=[]
        HarvDay=[]
        Meas=[]
        Mod=[]
        MeasU=[]
        ModU=[]
        MeasL=[]
        ModL=[]
        MeasQ=[]
        ModQ=[]
        Error=[]
        for row in rows:
            Eco.append(row[3])
            Lat.append(row[4])
            Long.append(row[5])
            Precip.append(row[6])
            GDD.append(row[7])
            Sand.append(row[8])
            LCC.append(row[9])
            Nrate.append(row[10])
            HarvDay.append(row[11])
            Meas.append(row[13])
            Mod.append(row[14])
            Error.append(row[15])
            if row[3]=='U':
                MeasU.append(row[13])
                ModU.append(row[14])
            elif row[3]=='L':
                MeasL.append(row[13])
                ModL.append(row[14])
            else:
                MeasQ.append(row[13])
                ModQ.append(row[14])
            c.writerow(row)

    #query treatment-averaged results
    with con:
        cur = con.cursor()
        cur.execute("SELECT a.Study, a.Site, a.Treatment, t.Ecotype, a.Avg_yield, \
                     AVG((m.crmvst/%s)*0.01), \
                     AVG(((((m.crmvst/.45)*0.01)-a.Avg_yield)/a.Avg_yield)) \
                     FROM Avg_meas a \
                     JOIN Modeled m ON a.Study=m.Study AND a.Site=m.Site \
                                    AND a.Treatment=m.Treatment \
                     JOIN Treatments t ON a.Study=t.Study \
                                    AND a.Treatment=t.Treatment\
                     GROUP BY a.Study, a.Site, a.Treatment \
                     ORDER BY a.Study, a.Site, a.Treatment" % (c_conc))
        rows = cur.fetchall()
        c = csv.writer(open(logfile, "a"))
        print "Results log '"+logfile+"' being updated..."
        print
        Meas_avg=[]
        Mod_avg=[]
        MeasU_avg=[]
        ModU_avg=[]
        MeasL_avg=[]
        ModL_avg=[]
        MeasQ_avg=[]
        ModQ_avg=[]
        for row in rows:
            Meas_avg.append(row[4])
            Mod_avg.append(row[5])
            if row[3]=='U':
                MeasU_avg.append(row[4])
                ModU_avg.append(row[5])
            elif row[3]=='L':
                MeasL_avg.append(row[4])
                ModL_avg.append(row[5])
            else:
                MeasQ_avg.append(row[4])
                ModQ_avg.append(row[5])            
            c.writerow(row)

    #plot results
    MMplot(Meas, Mod, MeasU, ModU, MeasL, ModL, MeasQ, ModQ, \
           "Measured-v-modeled_annual.png")
    MMplot(Meas_avg, Mod_avg, MeasU_avg, ModU_avg, MeasL_avg, ModL_avg, MeasQ_avg, \
           ModQ_avg, "Measured-v-modeled_treatment-averaged.png")
    EvXplot (Error, Lat, 'Latitude (deg)', "Error-v-Latitude.png")
    EvXplot (Error, Long, 'Longitude (deg)', "Error-v-Longitude.png")
    EvXplot (Error, Precip, 'Average annual precipitation (cm/y)', "Error-v-Precip.png")
    EvXplot (Error, GDD, 'Average annual growing degree days (GDD)', "Error-v-GDD.png")
    EvXplot (Error, Sand, 'Soil sand fraction (%)', "Error-v-Sand.png")
    EvXplot (Error, LCC, 'Non-irrigated land capability class rating (LCC)', "Error-v-LCC.png")
    EvXplot (Error, Nrate, 'Nitrogent application rate (gN/m2)', "Error-v-N.png")
    EvXplot (Error, HarvDay, 'Harvest day of the year', "Error-v-Harv.png")
