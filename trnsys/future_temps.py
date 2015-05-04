import pandas as pd
import numpy as np
import netCDF4

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

d1 = netCDF4.Dataset('/home/melchior/Data/ehe_data/EHE_analysis/by_folder_number/tasmax_1.nc')
d2 = netCDF4.Dataset('/home/melchior/Data/ehe_data/EHE_analysis/by_folder_number/tasmax_2.nc')

d5 = netCDF4.Dataset('/home/melchior/Data/ehe_data/EHE_analysis/by_folder_number/tasmax_5.nc')
d6 = netCDF4.Dataset('/home/melchior/Data/ehe_data/EHE_analysis/by_folder_number/tasmax_6.nc')

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
