import pandas as pd
import numpy as np
import netCDF4

##############################################
# GET 97.5TH PERCENTILE FOR FUTURE SCENARIOS #
##############################################

d = {
1: [2030,'la'],
2: [2010, 'la'],
3: [2050, 'phx'],
4: [2070, 'phx'],
5: [2010, 'phx'],
6: [2030, 'phx'],
7: [2050, 'la'],
8: [2070, 'la']
}

d1 = netCDF4.Dataset('tasmax_1.nc')
d2 = netCDF4.Dataset('tasmax_2.nc')

d5 = netCDF4.Dataset('tasmax_5.nc')
d6 = netCDF4.Dataset('tasmax_6.nc')

proj = pd.Series(d1.Projections.split(',')).str.strip()[:-1]
projsel = proj[proj.str.contains('csiro-mk3-6-0.5.rcp4|mpi-esm-lr.2.rcp4|gfdl-esm2g.1.rcp4')]

#LA, 2010-2050

for k, v in projsel.iteritems():
    cat = np.concatenate([np.ma.filled(d2.variables['tasmax'][k,:,:,:], np.nan), np.ma.filled(d1.variables['tasmax'][k,:,:,:], np.nan)])
    df = pd.DataFrame(np.percentile(cat, 97.5, axis=0), index=d1.variables['latitude'][:], columns=d1.variables['longitude'][:])
    df.to_csv('la_%s.csv' % v)

#PHX, 2010-2050

for k, v in projsel.iteritems():
    cat = np.concatenate([np.ma.filled(d5.variables['tasmax'][k,:,:,:], np.nan), np.ma.filled(d6.variables['tasmax'][k,:,:,:], np.nan)])
    df = pd.DataFrame(np.percentile(cat, 97.5, axis=0), index=d5.variables['latitude'][:], columns=d5.variables['longitude'][:])
    df.to_csv('phx_%s.csv' % v)

#########################
# JOIN TO CENSUS TRACTS #
#########################

import geopandas as gpd
import pandas as pd
import numpy as np
from shapely import geometry
from geopandas import tools

#### LOS ANGELES

la = gpd.read_file('tl_2010_06_tract10.shp')
la = la.loc[la['COUNTYFP10'] == '037']

la_dict = {
'echam' : pd.read_csv('la_mpi-esm-lr.2.rcp45.csv', index_col=0),
'gfdl' : pd.read_csv('la_gfdl-esm2g.1.rcp45.csv', index_col=0),
'csiro' : pd.read_csv('la_csiro-mk3-6-0.5.rcp45.csv', index_col=0)
}

for i in la_dict.keys():
    la_dict[i] = la_dict[i].stack().reset_index().astype(float)
    la_dict[i]['level_1'] = la_dict[i]['level_1'] - 360
    la_dict[i] = gpd.GeoDataFrame(la_dict[i][0], geometry=la_dict[i][['level_1', 'level_0']].apply(tuple, axis=1).apply(geometry.Point)).rename(columns={0:i})
    la_dict[i].crs = la.crs
    la_dict[i] = la.centroid.apply(lambda x: x.coords[0]).apply(lambda x: list(la_dict[i].sindex.nearest(x, 1, objects='raw'))[0]).map(la_dict[i][i])
    la_dict[i].name = i

la_out = pd.concat(la_dict.values(), axis=1)
la_out = pd.concat([la_out, la['TRACTCE10']], axis=1).set_index('TRACTCE10')
la_out.to_csv('la_census_975pct_2010_2050.csv')

#### PHOENIX

phx = gpd.read_file('tl_2010_04_tract10.shp')
phx = phx.loc[phx['COUNTYFP10'] == '013']

phx_dict = {
'echam' : pd.read_csv('phx_mpi-esm-lr.2.rcp45.csv', index_col=0),
'gfdl' : pd.read_csv('phx_gfdl-esm2g.1.rcp45.csv', index_col=0),
'csiro' : pd.read_csv('phx_csiro-mk3-6-0.5.rcp45.csv', index_col=0)
}

for i in phx_dict.keys():
    phx_dict[i] = phx_dict[i].stack().reset_index().astype(float)
    phx_dict[i]['level_1'] = phx_dict[i]['level_1'] - 360
    phx_dict[i] = gpd.GeoDataFrame(phx_dict[i][0], geometry=phx_dict[i][['level_1', 'level_0']].apply(tuple, axis=1).apply(geometry.Point)).rename(columns={0:i})
    phx_dict[i].crs = phx.crs
    phx_dict[i] = phx.centroid.apply(lambda x: x.coords[0]).apply(lambda x: list(phx_dict[i].sindex.nearest(x, 1, objects='raw'))[0]).map(phx_dict[i][i])
    phx_dict[i].name = i

phx_out = pd.concat(phx_dict.values(), axis=1)
phx_out = pd.concat([phx_out, phx['TRACTCE10']], axis=1).set_index('TRACTCE10')
phx_out.to_csv('phx_census_975pct_2010_2050.csv')
