import os
import numpy as np
import pandas as pd
import pickle
import netCDF4
import datetime

### CREATE SOLAR DF

class make_solar():
	def __init__(self, eiapath='/home/melchior/Desktop/eia8602012'):
		gen = pd.read_excel('%s/GeneratorY2012.xlsx' % (eiapath), skiprows=1)
		plant = pd.read_excel('%s/PlantY2012.xlsx' % (eiapath), skiprows=1)

		pcodes = gen.loc[gen['Prime Mover'].isin(['PV', 'CP'])]['Plant Code'].unique()

		solar_plants = plant.set_index('Plant Code').loc[pcodes]
		wecc_solar_plants = solar_plants.loc[solar_plants['NERC Region'] == 'WECC']

		wecc_solar_ll = zip(wecc_solar_plants['Latitude'], wecc_solar_plants['Longitude'])

		wecc_solar_pcodes = wecc_solar_plants.index

		solar_gen = gen.loc[gen['Prime Mover'].isin(['PV', 'CP'])].groupby('Plant Code').sum()['Nameplate Capacity (MW)'].loc[wecc_solar_pcodes]

		self.solar = pd.concat([solar_gen, solar_plants['Latitude'], solar_plants['Longitude']], axis=1, join='inner')

		westbound = int(self.solar['Longitude'].min()) - 1
		eastbound = int(self.solar['Longitude'].max()) + 1
		northbound = int(self.solar['Latitude'].max()) + 1
		southbound = int(self.solar['Latitude'].min()) - 1

		lats = pd.Series(np.arange(southbound, northbound, 0.0625)[1:][::2])
		longs = pd.Series(np.arange(westbound, eastbound, 0.0625)[1:][::2])

		self.solar['lat_grid'] = 0.0
		self.solar['lon_grid'] = 0.0

		for i in self.solar.index:
			sitelat = self.solar.loc[i, 'Latitude']
			sitelon = self.solar.loc[i, 'Longitude']
			lat_grid = lats.loc[abs((lats - sitelat)).idxmin()]
			lon_grid = longs.loc[abs((longs - sitelon)).idxmin()]
			self.solar.loc[i, 'lat_grid'] = lat_grid
			self.solar.loc[i, 'lon_grid'] = lon_grid

		##########SUNY GRID FOR SOLAR RADIATION

		lats_suny = pd.Series(np.arange(southbound, northbound, 0.05)[1:][::2])
		longs_suny = pd.Series(np.arange(westbound, eastbound, 0.05)[1:][::2])

		self.solar['lat_suny'] = 0.0
		self.solar['lon_suny'] = 0.0

		for i in self.solar.index:
			sitelat = self.solar.loc[i, 'Latitude']
			sitelon = self.solar.loc[i, 'Longitude']
			lat_grid = lats_suny.loc[abs((lats_suny - sitelat)).idxmin()]
			lon_grid = longs_suny.loc[abs((longs_suny - sitelon)).idxmin()]
			self.solar.loc[i, 'lat_suny'] = lat_grid
			self.solar.loc[i, 'lon_suny'] = lon_grid

		#########################################

		self.basin_masks = pickle.load(open('/media/melchior/BALTHASAR/nsf_hydro/pre/source_data/source_proj_forcings/active/basin_masks.p', 'r')) 

		###GET SOLAR COORDS IN EACH BASIN

		coord_li = list(set(['%s_%s' % (self.solar.loc[i, 'lat_grid'], self.solar.loc[i, 'lon_grid']) for i in self.solar.index]))

		self.reg_d = {}

		for j in self.basin_masks.keys():
			self.reg_d.update({j : {'coords':[], 'ix':[]}})

		for i in coord_li:
			for j in self.basin_masks.keys():
				if i in self.basin_masks[j]['coords']:
					self.reg_d[j]['coords'].append(i)
					self.reg_d[j]['ix'].append(self.basin_masks[j]['ix'][self.basin_masks[j]['coords'].index(i)])

	####EXTRACT FROM NETCDF FILES

	def extract_solar_hist(self, basin, inpath, outpath):
		outfile = outpath + '/hist'
		if not os.path.exists(outfile):
			os.mkdir(outfile)
		coords = self.reg_d[basin]['coords']
		file_li = ['data_%s' % (i) for i in coords]
		for fn in file_li:
			df = pd.read_csv('%s/%s' % (inpath, fn), sep='\t', header=None, index_col=False, names=['yr', 'mo', 'day', 'prcp', 'tmax', 'tmin', 'wind'])
			df = df.sort(['yr', 'mo', 'day'])[['yr', 'mo', 'day', 'prcp', 'tmax', 'tmin', 'wind']]
			df.to_csv('%s/%s' % (outfile, fn), sep='\t', header=False, index=False)

	def extract_solar_nc(self, scen, model, basin, outpath, master_path='/media/melchior/BALTHASAR/nsf_hydro/pre/source_data/source_proj_forcings/active/master'):

		outfile = outpath + '/' + model + '_' + scen
		if not os.path.exists(outfile):
			os.mkdir(outfile)

		coords = self.reg_d[basin]['coords']
		
		for i in range(len(coords)):
			c = coords[i]
			ix = self.reg_d[basin]['ix'][i]
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
			df['year'] = [j.year for j in df.index]
			df['month'] = [j.month for j in df.index]
			df['day'] = [j.day for j in df.index]
			df = df.sort(['year', 'month', 'day'])[['year', 'month', 'day', 'prcp', 'tmax', 'tmin', 'wind']]
			df.to_csv('%s/data_%s' % (outfile, coords[i]), sep='\t', index=False, header=False)


#### COMBINE CURVE WITH TEMPERATURE FORCINGS

	def make_solar_outfiles(self, sunypath, forcingpath, outpath):
		for i in self.solar.index:
			forcingstr = 'data_%s_%s' % (self.solar.loc[i, 'lat_grid'], self.solar.loc[i, 'lon_grid'])
			sunystr = 'SUNY_%s%s.csv' % (str(abs(self.solar.loc[i, 'lon_suny'])).replace('.', ''), str(abs(self.solar.loc[i, 'lat_suny'])).replace('.', ''))
		
			suny = pd.read_csv('%s/%s' % (sunypath, sunystr))

			suny = suny.drop(suny.loc[suny['Uglo'] < 0].index)

			suny['date'] = pd.to_datetime(suny['Date'])
			del suny['Date']

			suny['year'] = [j.year for j in suny['date']]
			suny['month'] = [j.month for j in suny['date']]
			suny['day'] = [j.day for j in suny['date']]

			a = suny.groupby(['year', 'month', 'day']).max().reset_index()
			b = a.groupby(['month', 'day']).mean()
			dmax = pd.rolling_mean(b['Uglo'], 14).fillna(pd.rolling_mean(b['Uglo'].iloc[-(14+1):].append(b['Uglo'].iloc[:14]), 14)).reset_index().rename(columns={0:'Uglo'})

			for scen in ['hist', 'ukmo_a1b', 'ukmo_a2', 'ukmo_b1', 'echam_a1b', 'echam_a2', 'echam_b1']:
				forcing = pd.read_csv('%s/%s/%s' % (forcingpath, scen, forcingstr), sep='\t', header=False, names=['year', 'month', 'day', 'prcp', 'tmax', 'tmin', 'wspd'])[['year', 'month', 'day', 'tmax']]
				
				m = pd.merge(dmax, forcing, on=['month', 'day']).sort(['year', 'month', 'day'])

				m['CAP_MW'] = self.solar.loc[i,'Nameplate Capacity (MW)']*(m['Uglo']/1000.0)*(1-0.0045*(m['tmax'] - 25.0))
				m['CAP_MW'].loc[m['CAP_MW'] >= self.solar.loc[i,'Nameplate Capacity (MW)']] = self.solar.loc[i,'Nameplate Capacity (MW)']  
				m = m[['year', 'month', 'day', 'CAP_MW']]
				m.to_csv('%s/%s/%s.%s' % (outpath,scen,scen,i) , sep='\t')

#####################################################

#for x in b.reg_d.keys():
#	b.extract_solar_hist(x, '/media/melchior/BALTHASAR/nsf_hydro/pre/source_data/source_hist_forcings/active/master', '/home/melchior/Desktop/solar')

#for x in b.reg_d.keys():
#	for sc in ['a1b', 'a2', 'b1']:
#		for m in ['mpi_echam5.3', 'ukmo_hadcm3.1']:
#			b.extract_solar_nc(sc, m, x, '/home/melchior/Desktop/solar')

b = make_solar()
b.make_solar_outfiles('/home/melchior/Desktop/suny_solar', '/home/melchior/Desktop/solar', '/home/melchior/Desktop/solar_out')
