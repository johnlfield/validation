f=open("Boyer13_Milan-WDLU_N67.lis")
lines=f.readlines()
print lines[6]

"SELECT r.Run, s.mukey, s.NARRx, s.NARRy, s.Lat, s.Long, t.*, s.Site, s.ST \
                     FROM Yields y \
                     JOIN Sites s ON y.Site=s.Site \
                     JOIN Treatments t ON y.Treatment=t.Treatment AND y.Study=t.Study \
                     JOIN FIPS f ON s.ST=f.ST AND s.County=f.County \
                     JOIN runfile20130307 r ON f.FIPS=r.FIPS AND s.NARRx=r.NARRx \
                                            AND s.NARRy=r.NARRy AND s.mukey=r.mukey")
                                            
                                            

SELECT a.Study, a.Site, a.Treatment, t.Ecotype, s.Lat, s.Long, s.Avg_precip, s. Avg_GDD, s.sand, s.NI_LCC, t.SGN1_rate, t.Harv_DOY, a.Year, a.Yield, (m.crmvst/.45)*0.01, ((((m.crmvst/.45)*0.01)-a.Yield)/a.Yield) FROM Ann_meas a JOIN Modeled m ON a.Study=m.Study AND a.Site=m.Site AND a.Treatment=m.Treatment AND a.Year=m.time JOIN Sites s ON s.Study=a.Study AND s.Site=a.Site JOIN Treatments t ON t.Study=a.Study AND t.Treatment=a.Treatment WHERE a.Yield>0;

SELECT a.Study, a.Site, a.Treatment, t.Ecotype, s.Lat, s.Long, s.Avg_precip, s. Avg_GDD, s.sand, s.NI_LCC, t.SGN1_rate, t.Harv_DOY, a.Avg_yield, AVG((m.crmvst/.45)*0.01), AVG(((((m.crmvst/.45)*0.01)-a.Avg_yield)/a.Avg_yield)) FROM Avg_meas a JOIN Modeled m ON a.Study=m.Study AND a.Site=m.Site AND a.Treatment=m.Treatment JOIN Sites s ON s.Study=a.Study AND s.Site=a.Site JOIN Treatments t ON t.Study=a.Study AND t.Treatment=a.Treatment GROUP BY a.Treatment;

SELECT a.Study, a.Site, a.Treatment, a.Avg_yield, AVG((m.crmvst/.45)*0.01), AVG(((((m.crmvst/.45)*0.01)-a.Avg_yield)/a.Avg_yield)) FROM Avg_meas a JOIN Modeled m ON a.Study=m.Study AND a.Site=m.Site AND a.Treatment=m.Treatment GROUP BY a.Study, a.Site, a.Treatment ORDER BY a.Study, a.Site, a.Treatment;