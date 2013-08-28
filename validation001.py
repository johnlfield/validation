
# Copy CSV file contents into a SQLite database table 
def CSVtoDB(csvfile, dbfile, delim):
#arguments- CSV and DB filenames, NO EXTENSION!, delimiter: c=comma, t=tab
    import csv
    import sqlite3 as lite
    #copy CSV file contents into a python list
    if delim == "c":
        Lines = csv.reader(open(csvfile, 'rb'))
    elif delim == "t":
        Lines = csv.reader(open(csvfile, 'rb'), delimiter="\t")
    List = [[]]
    for x in Lines:
        List.append(x)
    #define SQL-format strings to create & populate table
    csv = csvfile[:-4]
    headerquery = "CREATE TABLE "+csv+"("
    insertquery = "INSERT INTO "+csv+" VALUES("
    dropquery = "DROP TABLE IF EXISTS "+csv
    for i in range(len(List[1])):           #transform column names & datatypes to string
        headerquery = headerquery+List[1][i]+" "+List[2][i]+", "
    headerquery = headerquery[:-2]+')'
    insertquery = insertquery+i*"?, " + "?)" 
    #clean up python list, deleting initialization row and three header rows
    for i in range(4):
        del List[0]
    #copy python list contents to a DB table
    #SQL table write structure from http://zetcode.com/db/sqlitepythontutorial/
    con = lite.connect(dbfile)              #establish database connection
    with con:
        cur = con.cursor()
        cur.execute(dropquery)
        cur.execute(headerquery)
        cur.executemany(insertquery, List)


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
print "If you would like to generate a new DayCent runtable, please enter the runtable"
print "archive number to use:"
runarch = raw_input()
if runarch != "":
    #specification of all relevant directory paths
    import os
    import glob
    import shutil
    abspath = os.path.abspath(__file__)     #get absolute path where script is located
    dname = os.path.dirname(abspath)        #associated directory only
    os.chdir(dname)
    os.chdir('..')
    os.chdir('..')                          #navigate TWO directories higher
    dirmain = os.getcwd()
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
        Database = "switch.db"
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
print "If you would like to analyze a DayCent results archive against 'Yields.csv',"
print "please enter the results archive number to use:"
analysis = raw_input()
if analysis != "":
    print
    script = os.path.basename(__file__)
    print "Code version:  ", script
    print
    print "ANALYSIS goes here... :)"
    print
    print    






# ### AUTOMATED DATA ANALYSIS
# 
# ### IMPORT, LABEL & CONCATENATE .LIS FILES
# os.chdir(dirarch)
# import numpy as np
# print
# print "Analyzing model runs for treatments:"
# i = 1
# for file in glob.glob(os.path.join(dirarch, '*')):
#     if file.endswith(".lis"):                        #for each .lis file in the archive 
#         base=os.path.basename(file)
#         filename = os.path.splitext(base)[0]         #split off the filename       
#         print filename
#         npdata = np.genfromtxt(file, skip_header=3)  #import .lis data as numpy array
#         listdata = npdata.tolist()                   #convert numpy array to Python list
#         for row in listdata:
#             row.insert(0, filename)                  #add treatment ID to each entry
#             row.append(0)                            #add a placeholder for measured yield
#         if i == 1:
#             table = listdata                         #initialize 'table' with first .lis file
#         else:
#             table = table+listdata                   #concatenate files
#         i += 1
# print
# 
# ### DELETE REDUNDENT .LIS ENTRIES, CONVERT CRMVST TO YIELD, REINDEX YEARS
# redun = True
# row = 0
# while row < (len(table)-1):                          #loop through the table
#     for i in range(3):
#         if table[row][i] != table[row+1][i]:         #if the first 4 elements are identical
#             redun = False                            #from this row to the next
#     if redun == True:
#         del table[row+1]                             #delete the next row
#     row += 1
# c_conc = 0.45                                        #define biomass carbon concentration
# for row in range(len(table)):
#     crmvst = table[row][6]                           #extract crmvst
#     year = table[row][1]
#     Mgha = round((crmvst/c_conc)*(1/100.0), 3)       #gC/m2 -> MgdryBM/ha unit conversion
#     table[row][6] = Mgha                             #replace crmvst with yield
#     year = int(year)-1                               #round and index back 1 year
#     table[row][1] = year                             #replace original year with reindexed
#  
# ### IMPORT MEASURED YIELDS, JOIN TO MODEL RESULTS
# os.chdir(dirmain)
# import csv
# yields = csv.reader(open('yields.csv', 'rb'))        #import yields.csv
# tab = [[]]                         #list to receive measurements (all years of a treatment)
# for row in yields:                 #convert each row of csv file values to a list element
#     tab.append(row)
# del tab[0]                         #delete the initialization row
# yie = [[]]                         #new list to receive separate entries for every year
# for row in range(len(tab)):        #loop through each treatment in tab[]
#     year = 1990
#     base = 1989
#     treat = tab[row][0]                     #extract the treatment name
#     while year <= 2013:                     #loop through every year w/in that treatment
#         meas = float(tab[row][year-base])   #extract the associated yield measurement as a float
#         if meas != 0.0:                     #if biomass was recorded that year    
#             entry = [treat, year, meas, 0]  #create a treatment-year-yield-modeled(placeholder) list
#             yie.append(entry)               #append to re-formatted 'measured' yields array
#         year += 1
# del yie[0]                                  #delete the initialization row
# for measu in range(len(yie)):               #for each entry in 'measured' yields array
#     for mod in range(len(table)):           #loop through every table entry
#         if yie[measu][0]==table[mod][0] and yie[measu][1]==table[mod][1]:     #if treat+year match
#             yie[measu][3] = table[mod][6]   #extract modeled yield, write to the placeholder       
# for j in range(10):         ### cheated here; 10 is an arbitrary # of loops cause I didn't have logic figured out...
#     i = 0
#     while i < len(yie):                             
#         if yie[i][3] == 0:
#             del yie[i]                      #get rid of entries where no modeled data available
#         i += 1
# print "Comparison points:"
# print "  (all yields in dry Mg/ha)"  
# print "[treatment, year, measured yield, modeled yield]:"
# for row in yie:
#     print row
# print
# 
# ### remaining piece #3 add capability to save a results file
# 
# ### ANALYZE & PLOT RESULTS
# #decompose final datatable yie[]
# treat = [[]]
# year = [[]]
# meas =[[]]
# mod = [[]]
# for i in range(len(yie)):
#     treat.append(yie[i][0])
#     year.append(yie[i][1])
#     meas.append(yie[i][2])
#     mod.append(yie[i][3])
# del meas[0]
# del mod[0]
# del treat[0]
# #generate datatable of averages across years for each treatment
# treatuniq = set(treat)            #list unique treatments by converting to set
# treatset = list(treatuniq)        #convert back to list format
# measavgs = [[]]
# modavgs = [[]]
# for treat in treatset:            #for every unique treatment
#     measset = [[]]
#     modset = [[]]
#     for i in range(len(yie)):     #loop through yie[] and list matching meas, mod results
#         if yie[i][0] == treat:
#             measset.append(yie[i][2])
#             modset.append(yie[i][3])
#     del measset[0]
#     del modset[0]
#     measavg = np.mean(measset)   #average across those lists
#     modavg = np.mean(modset)
#     measavgs.append(measavg)
#     modavgs.append(modavg)
# del measavgs[0]
# del modavgs[0]
# #compute annual, treatment-averaged RMSE values
# def rmse(listmeas,listmod):
#     sqerr = 0
#     for i in range(len(listmeas)):
#         sqerr += (listmod[i]-listmeas[i])**2
#     return (sqerr/float(len(listmeas)))**0.5
# RMSEannual = rmse(meas,mod)
# RMSEavg = rmse(measavgs,modavgs)
# #plot treatment averages
# import matplotlib.pyplot as plt
# plt.plot([0,25], [0,25])       
# plt.plot(measavgs, modavgs, 'ro')
# ###turn on point labeling by un-commenting below
# #for i in range(len(yie)):
# #    plt.annotate(treatset[i], xy = (measavgs[i], modavgs[i]), fontsize=7)
# plt.title(descr+", treatment averages")
# plt.xlabel('Measured switchgrass yield (dry Mg/ha)')
# plt.ylabel('Modeled switchgrass yield (dry Mg/ha)')
# plt.text(2, 21, "RMSE = "+str(round(RMSEavg,3))+" Mg/ha")
# os.chdir(dirarch)
# plt.show()
# sec = round((time.time() - start), 2)
# plt.savefig('Mod-v-meas(averaged).png')
# plt.close()
# #plot individual years
# plt.plot([0,25], [0,25])       
# plt.plot(meas, mod, 'ro')
# ###turn on point labeling by un-commenting below
# #for i in range(len(yie)):
# #    plt.annotate(treat[i], xy = (meas[i], mod[i]), fontsize=7)
# plt.title(descr+", annual results")
# plt.xlabel('Measured switchgrass yield (dry Mg/ha)')
# plt.ylabel('Modeled switchgrass yield (dry Mg/ha)')
# plt.text(2, 21, "RMSE = "+str(round(RMSEannual,3))+" Mg/ha")
# os.chdir(dirarch)
# plt.show()
# plt.savefig('Mod-v-meas(annual).png')
# 
# ### RUN SUMMARY
# secpertreat = round(sec/treatcount, 2)
# min = round(sec/60.0, 2)
# sec = str(sec)
# secpertreat = str(secpertreat)
# min = str(min)
# treatcount = str(treatcount)
# if bool(nospin) == True:
#     text = "appending *.bin files from archive "+tstamp+"."
# else:
#     text = "including full spin-ups."
# print "Analysis complete."
# print "It took "+min+" minutes total to run the "+treatcount+" treatments ("+secpertreat+" sec/treatment),"
# print text
# print