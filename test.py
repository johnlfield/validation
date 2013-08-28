import os
os.chdir('..')
os.chdir('..')
import sqlite3 as lite
con = lite.connect('switch.db')
with con:
    cur = con.cursor()
    cur.execute("SELECT y.Study, s.Site, y.Treatment, f.FIPS, r.Run \
                 FROM Yields y \
                 JOIN Sites s ON y.Study=s.Study AND y.Site=s.Site \
                 JOIN Treatments t ON y.Study=t.Study AND y.Treatment=t.Treatment \
                 JOIN FIPS f ON s.ST=f.ST AND s.County=f.County \
                 JOIN runfile20130307 r ON f.FIPS=r.FIPS AND s.NARRx=r.NARRx \
                                        AND s.NARRy=r.NARRy AND s.mukey=r.mukey")
    rows = cur.fetchall()
    for row in rows:
        print row