import os
import pandas as pd
import numpy as np

gen = pd.read_excel('/home/tabris/Desktop/EIA_form_data/eia_form_860/eia8602012/GeneratorY2012.xlsx', skiprows=1)
plant = pd.read_excel('/home/tabris/Desktop/EIA_form_data/eia_form_860/eia8602012/PlantY2012.xlsx', skiprows=1)

pcodes = gen.loc[gen['Prime Mover'].isin(['PV', 'CP'])]['Plant Code'].unique()

solar_plants = plant.set_index('Plant Code').loc[pcodes]
wecc_solar_plants = solar_plants.loc[solar_plants['NERC Region'] == 'WECC']

wecc_solar_ll = zip(wecc_solar_plants['Latitude'], wecc_solar_plants['Longitude'])

wecc_solar_pcodes = wecc_solar_plants.index

solar_gen = gen.loc[gen['Prime Mover'].isin(['PV', 'CP'])].groupby('Plant Code').sum()['Nameplate Capacity (MW)'].loc[wecc_solar_pcodes]

solar = pd.concat([solar_gen, solar_plants['Latitude'], solar_plants['Longitude']], axis=1, join='inner')

westbound = int(solar['Longitude'].min()) - 1
eastbound = int(solar['Longitude'].max()) + 1
northbound = int(solar['Latitude'].max()) + 1
southbound = int(solar['Latitude'].min()) - 1

lats = pd.Series(np.arange(southbound, northbound, 0.0625)[1:][::2])
longs = pd.Series(np.arange(westbound, eastbound, 0.0625)[1:][::2])

solar['lat_grid'] = 0.0
solar['lon_grid'] = 0.0

for i in solar.index:
    sitelat = solar.loc[i, 'Latitude']
    sitelon = solar.loc[i, 'Longitude']
    lat_grid = lats.loc[abs((lats - sitelat)).idxmin()]
    lon_grid = longs.loc[abs((longs - sitelon)).idxmin()]
    solar.loc[i, 'lat_grid'] = lat_grid
    solar.loc[i, 'lon_grid'] = lon_grid

##########SUNY GRID FOR SOLAR RADIATION

lats_suny = pd.Series(np.arange(southbound, northbound, 0.05)[1:][::2])
longs_suny = pd.Series(np.arange(westbound, eastbound, 0.05)[1:][::2])

solar['lat_suny'] = 0.0
solar['lon_suny'] = 0.0

for i in solar.index:
    sitelat = solar.loc[i, 'Latitude']
    sitelon = solar.loc[i, 'Longitude']
    lat_grid = lats_suny.loc[abs((lats_suny - sitelat)).idxmin()]
    lon_grid = longs_suny.loc[abs((longs_suny - sitelon)).idxmin()]
    solar.loc[i, 'lat_suny'] = lat_grid
    solar.loc[i, 'lon_suny'] = lon_grid


#######################################
import math
import subprocess as sub

basestr = 'ftp://ftp.ncdc.noaa.gov/pub/data/nsrdb-solar/SUNY-gridded-data'

for g in list(set(zip(solar['lat_suny'], solar['lon_suny']))):  
    lat = g[0]
    lon = g[1]
    grid_lats = range(24,51)[::2]
    grid_lons = range(66,129)[::2]
    closest_lat = max([i for i in grid_lats if i < lat])
    closest_lon = min([i for i in grid_lons if i > abs(lon)])
    dirstr = '%s%s' % (closest_lon, closest_lat)
    
    latstr = str(abs(lat)).replace('.', '')
    lonstr = str(abs(lon)).replace('.', '')

    filestr = 'SUNY_%s%s.csv.gz' % (lonstr, latstr)

    cmd = "wget --random-wait -P /home/tabris/Downloads/suny_solar/ %s/%s/%s" % (basestr, dirstr, filestr)
    sub.call(cmd, shell=True)

#    lats = list(set([int(i) for i in solar['lat_suny']]))
#    lons = list(set([int(i) for i in solar['lon_suny']]))
