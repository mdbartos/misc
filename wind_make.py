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
    turb_cap = 0.5*(i[1])*(i[2]**3)*(i[4])*1.2041/1000000
    mw = g.loc[i, 'MW_turbine']
    multiplier = mw/turb_cap
    print multiplier
