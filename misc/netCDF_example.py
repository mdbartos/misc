import numpy as np
import pandas as pd
from shapely import vectorized, geometry
import geopandas as gpd
import os

bbox = (240.9375, 33.4375, 243.1875, 34.9375)
step = 0.125

lats = (np.array(np.linspace(bbox[1], bbox[3],
	        int(1 + (bbox[3] - bbox[1])/step)), 
		dtype=np.float32))

lons = (np.array(np.linspace(bbox[0], bbox[2],
	        int(1 + (bbox[2] - bbox[0])/step)),
		dtype=np.float32) - 360)

homedir = os.path.expanduser('~')
climzone = gpd.read_file('%s/Dropbox/CA_Building_Standards_Climate_Zones/CA_Building_Standards_Climate_Zones.shp' % homedir).to_crs(epsg=4326)

latlon = np.vstack(np.dstack(np.meshgrid(lons, lats)))

result = climzone['geometry'].apply(lambda x: np.where(vectorized.contains(x, latlon[:,0], latlon[:,1]))[0])
result = result[result.apply(len) > 0]

# If you want the integer index -- as it would appear in np.meshgrid(lons, lats)
zone_to_idx = pd.Series(np.concatenate(result.values), index=np.repeat(result.index.values, result.apply(len)))

# If you want the x and y indices:
idx_xy = zone_to_idx.apply(lambda x: np.unravel_index(x, (lons.size, lats.size))).apply(pd.Series).rename(columns={0: 'x', 1: 'y'})
