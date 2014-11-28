import numpy as np
import pandas as pd
import os
import datetime

windpath = '/home/tabris/Dropbox/Southwest Heat Vulnerability Team Share/ppdb_data/USGS_wind.csv'

nrel_path = '/home/tabris/Downloads/nrel_wind'

df = pd.read_csv(windpath)

gmw = df.groupby(['nrel_idx', 'mpower_coeff', 'rated_wspd', 'tower_h', 'rotor_s_a']).sum()['MW_turbine']
gll = df.groupby(['nrel_idx', 'mpower_coeff', 'rated_wspd', 'tower_h', 'rotor_s_a']).last()[['lat_grid', 'lon_grid']]

g = pd.concat([gmw, gll], axis=1) 

timeslicer = pd.date_range(start=datetime.datetime(2040,1,1), end=datetime.datetime(2060,1,1), freq='10min')

for i in g.index:
    nrel_idx = i[0]
    mpower_coeff = i[1]
    rated_wspd = i[2]
    tower_h = i[3]
    rotor_s_a = i[4]
    lat_grid = g.loc[i, 'lat_grid']
    lon_grid = g.loc[i, 'lon_grid']
    
    turb_cap = 0.5*(i[1])*(i[2]**3)*(i[4])*1.2041/1000000
    mw = g.loc[i, 'MW_turbine']
    multiplier = mw/turb_cap
    print multiplier

########## NREL CURVE ##########################

    nrel_2004 = pd.read_csv('%s/%s/1114.csv' % (nrel_path, 2004), skiprows=1, names=['date', 'wind', 'mw', 'score', 'correct'])[['date', 'wind']]
    nrel_2005 = pd.read_csv('%s/%s/1114.csv' % (nrel_path, 2005), skiprows=1, names=['date', 'wind', 'mw', 'score', 'correct'])[['date', 'wind']]
    nrel_2006 = pd.read_csv('%s/%s/1114.csv' % (nrel_path, 2006), skiprows=1, names=['date', 'wind', 'mw', 'score', 'correct'])[['date', 'wind']]

    nrel = pd.concat([nrel_2004, nrel_2005, nrel_2006])
    nrel['date'] = pd.to_datetime(nrel['date'])
    h = df.groupby(['month', 'day', 'hour', 'minute']).mean()['wind']
    hmax = nrel.groupby(['month', 'day', 'hour', 'minute']).max()['wind'].values
    hmin = nrel.groupby(['month', 'day', 'hour', 'minute']).min()['wind'].values

######### GET FORCINGS #########################
    hist_forcings = pd.read_csv('full_data_%s_%s' % (lat_grid, lon_grid), skiprows=6, sep='\t', names=['year', 'month', 'day', 'out_wind', 'out_density', 'out_pressure', 'out_vp', 'out_air_temp'])[['year', 'month', 'day', 'out_density']].groupby(['year', 'month', 'day']).mean()
