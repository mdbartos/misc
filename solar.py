import os
import numpy as np
import pandas as pd
import pickle

### CREATE SOLAR DF

gen = pd.read_excel('/home/akagi/Desktop/eia8602012/GeneratorY2012.xlsx', skiprows=1)
plant = pd.read_excel('/home/akagi/Desktop/eia8602012/PlantY2012.xlsx', skiprows=1)

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

#########################################

basin_masks = pickle.load(open('/home/akagi/Desktop/proj/basin_masks.p', 'r')) 

###GET SOLAR COORDS IN EACH BASIN

coord_li = list(set(['%s_%s' % (solar.loc[i, 'lat_grid'], solar.loc[i, 'lon_grid']) for i in solar.index]))

reg_d = {}

for j in basin_masks.keys():
	reg_d.update({j : {'coords':[], 'ix':[]}})

for i in coord_li:
	for j in basin_masks.keys():
		if i in basin_masks[j]['coords']:
			reg_d[j]['coords'].append(i)
			reg_d[j]['ix'].append(basin_masks[j]['ix'][basin_masks[j]['coords'].index(i)])

####EXTRACT FROM NETCDF FILES

master_path = '/media/melchior/BALTHASAR/nsf_hydro/pre/source_data/source_proj_forcings/active/master'

def extract_solar_hist(basin, inpath, outpath):
	outfile = outpath + '/hist'
	if not os.path.exists(outfile):
		os.mkdir(outfile)
	coords = reg_d[basin]['coords']
	file_li = ['data_%s' % (i) for i in coords]
	for fn in file_li:
		df = pd.read_csv('%s/%s' % (inpath, fn), sep='\t', header=None, index_col=False, names=['yr', 'mo', 'day', 'prcp', 'tmax', 'tmin', 'wind'])
		df = df[['prcp', 'tmax', 'tmin', 'wind']]
		df.to_csv('%s/%s' % (outfile, fn), sep='\t', header=False, index=False)

def extract_solar_nc(scen, model, basin, outpath):

	outfile = outpath + '/' + model + '_' + scen
	if not os.path.exists(outfile):
		os.mkdir(outfile)

	coords = reg_d[basin]['coords']
	
	for i in range(len(coords)):
		c = coords[i]
		ix = reg_d[basin]['ix'][i]
		df = pd.DataFrame()

		for y in range(2010,2100):
			year_df = pd.DataFrame()

			for v in ['prcp', 'tmax', 'tmin', 'wind']:
				f = netCDF4.Dataset('%s/%s.sres%s.%s.daily.%s.%s.nc' % (master_path, basin, scen, model, v, y) , 'r')
				s = f.variables[v][:, ix[0], ix[1]]
				year_df[v] = s
				f.close()

			year_df.index = pd.date_range(start=datetime.date(y,1,1), end=datetime.date(y,12,31))
			df = df.append(year_df)
		df = df[['prcp', 'tmax', 'tmin', 'wind']]
		df.to_csv('%s/data_%s' % (outfile, coords[i]), sep='\t', index=False, header=False)


#### COMBINE CURVE WITH TEMPERATURE FORCINGS

sunypath = '/home/akagi/Desktop/suny_solar/'
sunyfile = 'SUNY_103153215.csv'
suny = pd.read_csv('%s/%s' % (sunypath, sunyfile))

suny = suny.drop(suny.loc[suny['Uglo'] < 0].index)

suny['date'] = pd.to_datetime(suny['Date'])
#suny['doy'] = [i.timetuple().tm_yday for i in suny['date']]
del suny['Date']

suny['year'] = [i.year for i in suny['date']]
suny['month'] = [i.month for i in suny['date']]
suny['day'] = [i.day for i in suny['date']]

a = suny.groupby(['year', 'month', 'day']).max().reset_index()
b = a.groupby(['month', 'day']).mean()
dmax = pd.rolling_mean(b['Uglo'], 14).fillna(pd.rolling_mean(b['Uglo'].iloc[-(14+1):].append(b['Uglo'].iloc[:14]), 14)).reset_index().rename(columns={0:'Uglo'})

forcing = pd.read_csv('/home/akagi/Desktop/hist/data_36.4375_-119.6875', sep='\t', header=False, names=['year', 'month', 'day', 'prcp', 'tmax', 'tmin', 'wspd'])[['year', 'month', 'day', 'tmax']]

m = pd.merge(dmax, forcing, on=['month', 'day']).sort(['year', 'month', 'day'])

m['CAP_MW'] = (m['Uglo']/1000.0)*0.12*(1-0.0045*(m['tmax'] - 25.0))

#####################################################

for b in reg_d.keys():
	extract_wind_hist(b, '/media/melchior/BALTHASAR/nsf_hydro/pre/source_data/source_hist_forcings/active/master', '/home/melchior/Desktop/wind_new')

#for b in reg_d.keys():
#	for sc in ['a1b', 'a2', 'b1']:
#		for m in ['mpi_echam5.3', 'ukmo_hadcm3.1']:
#			extract_wind_nc(sc, m, b, '/home/melchior/Desktop/wind')

