import pandas as pd
import numpy as np

tracts = pd.read_csv('/home/akagi/Desktop/az_census_tracts.txt')
tracts['lon'] = tracts['lon'] + 360

phx_parcels = pd.read_csv('/home/akagi/Dropbox/Southwest Heat Vulnerability Team Share/EHE_days/phx/historical/EHE-phx_hist.csv')

ll = phx_parcels.groupby(['latitude', 'longitude']).mean().reset_index()[['latitude', 'longitude']]

tracts['grid_lat'] = 0.0
tracts['grid_lon'] = 0.0

for i in tracts.index:
	tracts.loc[i, ['grid_lat', 'grid_lon']] = ll.loc[ll.apply(lambda x: ((x['latitude'] - tracts.loc[i, 'lat'])**2 + (x['longitude'] - tracts.loc[i, 'lon'])**2)**0.5, axis=1).idxmin()].values
	print tracts.loc[i, ['grid_lat', 'grid_lon']]

