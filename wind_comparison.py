import numpy as np
import pandas as pd
import os
import datetime

histo = pd.read_csv('./hist/data_39.8125_-104.8125', sep='\t', names=['prcp', 'tmax', 'tmin', 'wspd'])
echam_a1b = pd.read_csv('./mpi_echam5.3_a1b/data_39.8125_-104.8125', sep='\t', names=['prcp', 'tmax', 'tmin', 'wspd'])
ukmo_a1b = pd.read_csv('./ukmo_hadcm3.1_a1b/data_39.8125_-104.8125', sep='\t', names=['prcp', 'tmax', 'tmin', 'wspd'])

histo['date'] = pd.date_range(start=datetime.date(1949, 1, 1), end=datetime.date(2010,12,31))
echam_a1b['date'] = pd.date_range(start=datetime.date(2010, 1, 1), end=datetime.date(2099,12,31))
ukmo_a1b['date'] = pd.date_range(start=datetime.date(2010, 1, 1), end=datetime.date(2099,12,31))

histo['month'] = [i.month for i in histo['date']]
histo['day'] = [i.day for i in histo['date']]
echam_a1b['month'] = [i.month for i in echam_a1b['date']]
echam_a1b['day'] = [i.day for i in echam_a1b['date']]
ukmo_a1b['month'] = [i.month for i in ukmo_a1b['date']]
ukmo_a1b['day'] = [i.day for i in ukmo_a1b['date']]

h = histo.groupby(['month', 'day']).mean().reset_index()
u = ukmo_a1b.groupby(['month', 'day']).mean().reset_index()
e = echam_a1b.groupby(['month', 'day']).mean().reset_index()
c = pd.concat([h['wspd'], u['wspd'], e['wspd']], axis=1)

quanthist = [histo['wspd'].quantile(float(i)/100) for i in range(1, 101)]
quantukmo = [ukmo_a1b['wspd'].quantile(float(i)/100) for i in range(1, 101)]
quantecham = [echam_a1b['wspd'].quantile(float(i)/100) for i in range(1, 101)]

quanthistc = [c.iloc[:,0].quantile(float(i)/100) for i in range(1, 101)]
quantukmoc = [c.iloc[:,1].quantile(float(i)/100) for i in range(1, 101)]
quantechamc = [c.iloc[:,2].quantile(float(i)/100) for i in range(1, 101)]

#plot(range(len(quanthist)), quanthist)
#hist(histo['wspd'], bins=100)
#hist(ukmo_a1b['wspd'].iloc[:22645], bins=100, alpha=0.75)

