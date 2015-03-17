import numpy as np
import pandas as pd
import ftplib as ftp
import subprocess as sub

inv = pd.read_fwf('./Desktop/ghcnd-inventory.txt', names=['id', 'lat', 'lon', 'var', 'start', 'end'])[['id', 'var', 'start', 'end']]
sta = pd.read_fwf('./Desktop/ghcnd-stations.txt', colspecs=[(0,11), (12,20), (21,30), (31,37), (38,40), (41,71), (72,75), (76,79), (80,85)], names=['id', 'lat', 'lon', 'elev', 'state', 'name', 'gsn', 'hcn', 'wmo'])

combined = pd.merge(sta, inv, on='id')

az = combined.loc[(combined['state']=='AZ') & (combined['var']=='TMAX') & (combined['start'] <= 1960) & (combined['end'] >= 2010)]

phx = az.loc[(az['lat'] <= 34.0) & (az['lon'] <= -111.2) & (az['lat'] >= 32.8) & (az['lon'] >= -112.8)]

#conn = ftp.FTP('ftp.ncdc.noaa.gov')
#conn.login()
#conn.cwd('pub/data/ghcn/daily')

basepath = 'ftp://ftp.ncdc.noaa.gov/pub/data/ghcn/daily/all/'

for i in az['id'].unique():
    cmd = "wget --random-wait -P /home/akagi/Downloads/az_ncdc/ %s/%s.dly" % (basepath, i)
    sub.call(cmd, shell=True)

