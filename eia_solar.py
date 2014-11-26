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


