
# Compute root-mean-square error
def rmse(meas,mod):
    sqerr = 0
    for i in range(len(meas)):
        sqerr += (mod[i]-meas[i])**2
    return (sqerr/float(len(meas)))**0.5
    
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
def MMplot (meas, mod, measU, modU, measL, modL, measQ, modQ, descrip, filename):
    import matplotlib.pyplot as plt
    from scipy import stats
    plt.plot([0,30], [0,30], color="black")       
    plt.plot(measL, modL, 'go', label='Lowland')
    plt.plot(measU, modU, 'ro', label='Upland')
    plt.plot(measQ, modQ, 'bo', label='unspecified')
    plt.legend()
    plt.title(filename[:-4]+'\n'+descrip)
    plt.xlabel('Measured switchgrass yield (dry Mg/ha)')
    plt.ylabel('Modeled switchgrass yield (dry Mg/ha)')
    slope, intercept, r_value, p_value, std_err = stats.linregress(meas,mod)
    RMSE=rmse(meas,mod)
    n = len(meas)
    miny=min(mod)
    maxy=max(mod)
    minx=min(meas)
    maxx=max(meas)
    plt.text(2, 22, 'Combined regression statistics: \nPearson correlation coefficient=%s \
                     \nRegression p-value=%s \nR2 value (non-adjusted)=%s \
                     \nRMSE=%s \nn=%s' % (round(r_value,3),round(p_value,4),\
                     round(r_value**2,3),round(RMSE,3),n))
    plt.plot([minx,maxx], [intercept+slope*minx,intercept+slope*maxx], color="grey")
    plt.savefig(filename)
    plt.close()
    return "n="+str(n)+", R2="+str(round(r_value**2,3))+", RMSE="+str(round(RMSE,3))

#plot error regressed versus X
def EvXplot(resid, regressor, label, descrip, filename):
    import matplotlib.pyplot as plt
    from scipy import stats      
    plt.plot(regressor, resid, 'go')
    plt.title(filename[:-4]+'\n'+descrip)
    plt.xlabel(label)
    plt.ylabel('Residual yield error (dry Mg/ha)')
    slope, intercept, r_value, p_value, std_err = stats.linregress(regressor,resid)
    n = len(resid)
    miny=min(resid)
    maxy=max(resid)
    minx=min(regressor)
    maxx=max(regressor)
    plt.text(.03*(maxx-minx)+minx, .8*(maxy-miny)+miny, 'Combined regression statistics: \
             \nPearson correlation coefficient=%s \nP-value=%s \nn=%s' \
             % (round(r_value,3),round(p_value,4),n))
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
    outfileC = "runtable_"+runarch+"_C.csv"
    outfileV = "runtable_"+runarch+"_V.csv"
    print
    
    #if the file described doesn't already exist, generate it 
    #otherwise, return an error and move on
    if os.path.exists(dirrun+"/"+outfileC) or os.path.exists(dirrun+"/"+outfileV): 
        print "** Runtable files already exist in the specified runtable archive;"
        print "       runtable generation terminated **"
        print
        print
    else:
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

        import csv
        import sqlite3 as lite
        for cal_val in ('C', 'V'):
            con = lite.connect(Database)
            cal_val = '"'+cal_val+'"'
            if cal_val=='"C"':
                outfile = outfileC
            elif cal_val=='"V"':
                outfile = outfileV
            print "Joining tables to generate DayCent runtable..."
            print
            with con:
                cur = con.cursor()
                cur.execute("SELECT r.Run, s.mukey, s.NARRx, s.NARRy, s.Lat, s.Long, t.*, s.Site, s.ST \
                            FROM Yields y \
                            JOIN Sites s ON y.Site=s.Site \
                            JOIN Treatments t ON y.Treatment=t.Treatment AND y.Study=t.Study \
                            JOIN FIPS f ON s.ST=f.ST AND s.County=f.County \
                            JOIN runfile20130307 r ON f.FIPS=r.FIPS AND s.NARRx=r.NARRx \
                                                   AND s.NARRy=r.NARRy AND s.mukey=r.mukey \
                            WHERE y.cal_val=%s" % (cal_val))
                rows = cur.fetchall()
                c = csv.writer(open(outfile, "wb"))
                print "Runtable "+outfile+" being saved:"
                for row in rows:
                    print row
                    c.writerow(row)
                shutil.move(outfile, dirrun)
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
    print "Please enter a brief description of the analysis to be used in plot titles and"
    print "the logbook entry: "
    descrip = raw_input()
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
        entry = [row[0], row[1], row[2], row[3], row[4]]
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
            for j in range(24):
                year = temp[0][j+5]
                year = year[1:]
                entry = [temp[i][0], temp[i][1], temp[i][2], year, temp[i][j+5]]
                annmeas.append(entry)
        i += 1
    os.chdir(dirmain)
    PyListoDB(annmeas, Database, 'Ann_meas')

    #query all annual measured yields, modeled yields, and supporting metadata
    c_conc = 0.45                          #define biomass carbon concentration
    import csv
    import sqlite3 as lite
    con = lite.connect(Database)
    with con:
        cur = con.cursor()
        cur.execute("SELECT a.Study, a.Site, a.Treatment, t.Ecotype, s.Lat, s.Long, \
                     s.Avg_precip, s. Avg_GDD, s.sand, s.NI_LCC, t.SGN1_rate, t.Harv_DOY, \
                     a.Year, a.Yield, (m.crmvst/%s)*0.01, \
                     (((m.crmvst/%s)*0.01)-a.Yield), a.Year-t.Est_year \
                     FROM Ann_meas a \
                     JOIN Modeled m ON a.Study=m.Study AND a.Site=m.Site AND \
                          a.Treatment=m.Treatment AND a.Year=m.time \
                     JOIN Sites s ON s.Study=a.Study AND s.Site=a.Site \
                     JOIN Treatments t ON t.Study=a.Study AND t.Treatment=a.Treatment \
                     WHERE a.Yield>0 AND m.time<2010 \
                     ORDER BY abs(((m.crmvst/%s)*0.01)-a.Yield) DESC" \
                     % (c_conc,c_conc,c_conc))
        rows = cur.fetchall()
        c = csv.writer(open("Annual_summary.csv", "wb"))
        
###update so that all .csv tables are re-loaded to the DB along with Yield.csv
## add metadata print out here!!!!
        print "Results log and summary results tables being saved..."
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
        Resid=[]
        PEY=[]
        headerstr=['Study','Site','Treatment','Ecotype','Lat','Long','Avg_precip',\
                   'Avg_GDD','sand','NI_LCC','SGN1_rate','Harv_DOY','Year',\
                   'Meas_yield','Mod_yield','Resid_error','PEY']
        c.writerow(headerstr)
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
            Resid.append(row[15])
            if row[3]=='U':
                MeasU.append(row[13])
                ModU.append(row[14])
            elif row[3]=='L':
                MeasL.append(row[13])
                ModL.append(row[14])
            else:
                MeasQ.append(row[13])
                ModQ.append(row[14])
            PEY.append(row[16])
            c.writerow(row)

    #query treatment-averaged results
    with con:
        cur = con.cursor()
        cur.execute("SELECT a.Study, a.Site, a.Treatment, t.Ecotype, s.Lat, s.Long, \
                     s.Avg_precip, s. Avg_GDD, s.sand, s.NI_LCC, t.SGN1_rate, t.Harv_DOY,\
                     a.Avg_yield, (m.crmvst/%s)*0.01, (((m.crmvst/%s)*0.01)-a.Avg_yield) \
                     FROM Avg_meas a \
                     JOIN Modeled m ON a.Study=m.Study AND a.Site=m.Site \
                                    AND a.Treatment=m.Treatment \
                     JOIN Sites s ON s.Study=a.Study AND s.Site=a.Site \
                     JOIN Treatments t ON t.Study=a.Study AND t.Treatment=a.Treatment \
                     WHERE a.Avg_yield>0 AND m.time<2010 \
                     GROUP BY a.Study, a.Site, a.Treatment \
                     ORDER BY abs(((m.crmvst/%s)*0.01)-a.Avg_yield) DESC" \
                     % (c_conc,c_conc,c_conc))
        rows = cur.fetchall()
        c = csv.writer(open("Treatment-averaged_summary.csv", "wb"))
        Eco_avg=[]
        Lat_avg=[]
        Long_avg=[]
        Precip_avg=[]
        GDD_avg=[]
        Sand_avg=[]
        LCC_avg=[]
        Nrate_avg=[]
        HarvDay_avg=[]
        Meas_avg=[]
        Mod_avg=[]
        MeasU_avg=[]
        ModU_avg=[]
        MeasL_avg=[]
        ModL_avg=[]
        MeasQ_avg=[]
        ModQ_avg=[]
        Resid_avg=[]
        headerstr=['Study','Site','Treatment','Ecotype','Lat','Long','Avg_precip',\
                   'Avg_GDD','sand','NI_LCC','SGN1_rate','Harv_DOY', 'Meas_yield',\
                   'Mod_yield','Resid_error']
        c.writerow(headerstr)           
        for row in rows:
            Eco_avg.append(row[3])
            Lat_avg.append(row[4])
            Long_avg.append(row[5])
            Precip_avg.append(row[6])
            GDD_avg.append(row[7])
            Sand_avg.append(row[8])
            LCC_avg.append(row[9])
            Nrate_avg.append(row[10])
            HarvDay_avg.append(row[11])
            Meas_avg.append(row[12])
            Mod_avg.append(row[13])
            if row[3]=='U':
                MeasU_avg.append(row[12])
                ModU_avg.append(row[13])
            elif row[3]=='L':
                MeasL_avg.append(row[12])
                ModL_avg.append(row[13])
            else:
                MeasQ_avg.append(row[12])
                ModQ_avg.append(row[13])            
            Resid_avg.append(row[14])
            c.writerow(row)

    #plot results (incl. basic stats)
    Ann_stats = MMplot(Meas, Mod, MeasU, ModU, MeasL, ModL, \
               MeasQ, ModQ, descrip, "Measured-v-modeled_annual.png")
    Avg_stats = MMplot(Meas_avg, Mod_avg, \
               MeasU_avg, ModU_avg, MeasL_avg, ModL_avg, MeasQ_avg, ModQ_avg, \
               descrip, "Measured-v-modeled_treatment-averaged.png")
    EvXplot(Resid_avg, Lat_avg, 'Latitude (deg)', descrip, "Error vs. Latitude.png")
    EvXplot(Resid_avg, Long_avg, 'Longitude (deg)', descrip, "Error vs. Longitude.png")
    EvXplot(Resid_avg, Precip_avg, 'Average annual precipitation (cm/y)', descrip, "Error vs. Average Annual Precipitation.png")
    EvXplot(Resid_avg, GDD_avg, 'Average annual growing degree days (GDD)', descrip, "Error vs. Average Annual GDD.png")
    EvXplot(Resid_avg, Sand_avg, 'Soil sand fraction (%)', descrip, "Error vs. Soil Sand Fraction.png")
    EvXplot(Resid_avg, LCC_avg, 'Non-irrigated land capability class rating (LCC)', descrip, "Error vs. LCC.png")
    EvXplot(Resid_avg, Nrate_avg, 'Nitrogen application rate (gN/m2)', descrip, "Error vs. N Rate.png")
    EvXplot(Resid_avg, HarvDay_avg, 'Harvest day of the year', descrip, "Error vs. Harvest Date.png")
    
    #add to log file and archive all plots
    import shutil
    import glob
    os.chdir(dirres)
    for g in glob.glob(os.path.join(dirres, '*')):
        if g.endswith(".txt"):
            logfile = os.path.basename(g)    
    d = open(logfile, "a")
    d.write("Analysis code version: "+script+'\n')
    d.write(""+'\n')
    d.write("Analysis description: "+descrip+'\n')
    d.write("Annual results regression stats: "+Ann_stats+'\n')
    d.write("Treatment-averaged results regression stats: "+Avg_stats)
    os.chdir(dirmain)
    for h in glob.glob(os.path.join(dirmain, '*')):
        if h.endswith(".png") or h.endswith(".csv"):  
            shutil.move(h, dirres)
