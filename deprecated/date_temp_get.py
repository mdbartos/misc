import pandas as pd
import numpy as np
import os
import datetime

df = pd.read_csv('/home/chesterlab/Desktop/ehe_dates.csv')
df['date'] = df['date'].apply(lambda x: datetime.datetime.strptime(x, '%m/%d/%Y'))
df['lon'] = df['lon'] - 360
df = pd.concat([df, df['date'].apply(lambda x: pd.Series([x.year, x.month, x.day])).rename(columns={0:'year', 1:'month', 2:'day'})], axis=1)

by_latlon = df.set_index('date').groupby(['lat', 'lon']).groups
    
basepath = '/home/chesterlab/Bartos/VIC/input/vic/forcing/hist/region/master'

out_df = pd.DataFrame(columns=['lat', 'lon', 'tmax', 'tmin'])

for i in by_latlon.keys():
    print i
    fn = '%s/data_%s_%s' % (basepath, i[0], i[1])
    forcing = pd.read_csv(fn, sep=' ', names=['prcp', 'tmax', 'tmin', 'wind'])
    forcing['date'] = pd.date_range(start=datetime.date(1949, 1, 1), end=datetime.date(2010, 12, 31)) 
    forcing = forcing.set_index('date')
    subset_days = forcing.loc[pd.Series(by_latlon[i])][['tmax', 'tmin']]
    subset_days['lat'] = i[0]
    subset_days['lon'] = i[1] + 360
    out_df = out_df.append(subset_days)
