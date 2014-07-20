import os
import pandas as pd
import numpy as np
import urllib2 as url
from StringIO import StringIO
import pickle
from datetime import date
from datetime import timedelta as td
import ast
from scipy.optimize import curve_fit
from scipy.stats import gaussian_kde

temp_d = pickle.load( open( "basin_temps.p", "rb"))
r_latlon = pickle.load( open( "region_latlon.p", "rb"))
latlon_d = pd.concat([i for i in r_latlon.values()], ignore_index=True)
latlon_d = latlon_d.drop_duplicates()


class make_mohseni():
	def __init__(self):
#		self.basin = basin
		self.len_d = {}
		self.max_d = {}
		self.loc_d = {}
		self.diff_d = {}
		self.param_d = {}
		self.cat_d = {}
		self.src_data = {}
		
	def find_max_station(self):
		for k in temp_d.keys():
			self.len_d.update({k : {}})
			self.max_d.update({k : None})
			print k
			for i, v in temp_d[k].items():
				self.len_d[k].update({i : len(v)})
			if len(self.len_d[k]) > 0:
				maxix = max(self.len_d[k], key=self.len_d[k].get)
				maxlen = max(self.len_d[k].values())
				print maxix, maxlen
				self.max_d[k] = maxix	

	def make_loc_d(self):
		for fn in os.listdir('.'):
			if fn.endswith('txt'):
				f = pd.read_csv(fn, dtype={'SITE_NO' : str})
				sn = f['SITE_NO']
				f['latlon'] = zip(f['LAT_SITE'], f['LON_SITE'])
				sf = fn.split('.')[0]
				self.loc_d.update({sf : f[['SITE_NO', 'latlon', 'STATION_NM']]})

	def relate_met(self, basin, **kwargs):
		print basin
		if kwargs['automax'] == True:
			st_id = self.max_d[basin]
		else:
			st_id = kwargs['st_id']
		if len(temp_d[basin]) > 0:
			self.diff_d.update({basin : {}})
			fn_d = {}
			ll = self.loc_d[basin]['latlon'].ix[self.loc_d[basin]['SITE_NO'] == st_id]
			print ll
			ll = tuple(ll.values)[0]
			lat = ll[0]
			lon = ll[1]
			for v in latlon_d.values:
				diff = ((v[0] - lat)**2 + (v[1] - lon)**2)**0.5
				fn_d.update({v : diff})
			cell = min(fn_d, key=fn_d.get)
			print cell
			mi = fn_d[cell]
			print mi
			self.diff_d[basin].update({st_id : cell})
		else:
			print 'no stations'			

	def cat_vars(self, basin, **kwargs):
		if len(self.diff_d[basin]) > 0:
			if kwargs['automax'] == True:
				st_id = self.max_d[basin]
			else:
				st_id = kwargs['st_id']
			w = temp_d[basin][st_id]
			diff_coords = self.diff_d[basin][st_id]
	#		print diff_coords
	#		print [i for i in t['datetime']]
			w['date'] = [(date(int(i.split('-')[0]), int(i.split('-')[1]), int(i.split('-')[2]))) for i in w['datetime']]
			tmax_str = [i for i in w.columns if '00010_00001' in i][0]
			tmin_str = [i for i in w.columns if '00010_00002' in i][0]
			tavg_str = [i for i in w.columns if '00010_00002' in i][0]
			w['w_tmax'] = w[tmax_str]
			w['w_tmin'] = w[tmin_str]
			w = w[['date', 'site_no','w_tmax', 'w_tmin']]
			w = w.set_index('date')
			w = w.replace(to_replace=['Ice'], value=[0.0])
			w['w_tmax'] = [float(i) for i in w['w_tmax']]
			w['w_tmin'] = [float(i) for i in w['w_tmin']]
			w['w_tavg'] = 0.5*(w['w_tmin'] + w['w_tmax'])
			a = pd.read_csv('./master/data_%s_%s' % (str(diff_coords[0]), str(diff_coords[1])), sep='\t', header=None, index_col=False, names=['year', 'month', 'day', 'prcp', 'tmax', 'tmin', 'wspd'])
			a['tavg'] = 0.5*(a['tmin'] + a['tmax'])
	#		d1 = date(1949, 1, 1)
	#		d2 = date(2010, 12, 31)
	#		ddelta = d2 - d1
	#		dr = [d1 + td(days=i) for i in range(ddelta.days + 1)]
	#		print len(dr)
	#		print a[['year', 'month', 'day']]
			a['date'] = [date(a['year'][i], a['month'][i], a['day'][i]) for i in a.index]
	#		print a['date']
			a = a.set_index('date')
			c = pd.concat([w,a], axis=1)
			print c
			self.cat_d.update({basin : {}})
			self.cat_d[basin].update({st_id : c})
			
		else:
			print 'No stations'

	def make_src_data(self, **src_kwargs):
		self.src_data = self.cat_d[src_kwargs['dbasin']][src_kwargs['dst_id']].dropna()		
		
	def mohseni(self, x, b, g):
		xdata = self.src_data['tavg']
		ydata = self.src_data['w_tavg']
		a = max(ydata)#.quantile(q=0.999)
		u = min(ydata)#.quantile(q=0.001)
		return u + (a-u)/(1 + np.exp(g*(b-x)))

	def fit_mohseni(self, basin, **kwargs):
		if kwargs['automax'] == True:
			st_id = self.max_d[basin]
		else:
			st_id = kwargs['st_id']
		self.make_src_data(dbasin=basin, dst_id=st_id)
		xdata = self.src_data['tavg']
		ydata = self.src_data['w_tavg']
		b_init = 12.0
		g_init = 0.2
		popt, pcov = curve_fit(self.mohseni, xdata, ydata, p0=[b_init, g_init])
		perr = np.sqrt(np.diag(pcov))
		self.param_d.update({basin : {}})
		self.param_d[basin].update({st_id : [popt, perr]})
		print popt, perr

	def filter_nan(s,o):
		"""
		this functions removed the data  from simulated and observed data
		whereever the observed data contains nan
		
		this is used by all other functions, otherwise they will produce nan as 
		output
		"""
		data = np.array([s,o])
		data = np.transpose(data)
		data = data[~np.isnan(data).any(1)]
		return data[:,0],data[:,1]

	def NS(self, s,o):
		"""
		Nash Sutcliffe efficiency coefficient
		input:
			s: simulated
			o: observed
		output:
			ns: Nash Sutcliffe efficient coefficient
		"""
		s,o = filter_nan(s,o)
		return 1 - sum((s-o)**2)/sum((o-np.mean(o))**2)

	def plot_curvefit(self, basin, **kwargs):
		if kwargs['automax'] == True:
			st_id = self.max_d[basin]
		else:
			st_id = kwargs['st_id']
		fig, ax = plt.subplots(1)
		xdata = self.src_data['tavg']
		ydata = self.src_data['w_tavg']
		xy = np.vstack([xdata, ydata])
		z = gaussian_kde(xy)(xy)
		ax.scatter(xdata, ydata, c=z, s=100, edgecolor='')
		ax.plot(arange(-20, 60), self.mohseni(arange(-20, 60), self.param_d[basin][st_id][0][0], self.param_d[basin][st_id][0][1]))
		statname = self.loc_d[basin]['STATION_NM'].ix[m.loc_d[basin]['SITE_NO'] == st_id]
		statname = statname.values[0]
		print statname
		title('USGS STATION %s, %s' % (self.max_d[basin], statname))
		xlabel('Air Temperature ($^\circ$C)')
		ylabel('Stream Temperature ($^\circ$C)')
#		textstr = r'$\beta=%.2f$\n$\gamma=%.2f$\n' % (self.param_d[basin][0][0], self.param_d[basin][0][1])
		textstr = '$\\alpha=%.2f$\n$\\beta=%.2f$\n$\\gamma=%.2f$\n$\\mu=%.2f$\n' % (max(self.src_data['w_tavg']), self.param_d[basin][st_id][0][0], self.param_d[basin][st_id][0][1], min(self.src_data['w_tavg']))
		props = dict(boxstyle='round', facecolor='wheat', alpha=0.5)
		ax.text(0.05, 0.95, textstr, transform=ax.transAxes, fontsize=14, verticalalignment='top', bbox=props)
		
	def prep_data(self, basin, **kwargs):
		self.find_max_station()
		self.make_loc_d()
		if kwargs['automax'] == True:
			self.relate_met(basin, automax=True)
			self.cat_vars(basin, automax=True)
		else:
			st_id = kwargs['st_id']
			self.relate_met(basin, automax=False, st_id=st_id)
			self.cat_vars(basin, automax=False, st_id=st_id)
		
	def reg_exec(self, basin, **kwargs):
		if kwargs['automax'] == True:
			self.fit_mohseni(basin, automax=True)
			self.plot_curvefit(basin, automax=True)
		else:
			st_id = kwargs['st_id']
			self.fit_mohseni(basin, automax=False, st_id=st_id)
			self.plot_curvefit(basin, automax=False, st_id=st_id)			
		

m = make_mohseni()
m.prep_data('lees_f', automax=True)
m.reg_exec('lees_f', automax=True)

m = make_mohseni()
m.prep_data('lees_f', automax=False, st_id='09095500')
m.reg_exec('lees_f', automax=False, st_id='09095500')

m = make_mohseni()
m.find_max_station()
m.make_loc_d()
m.relate_met('lees_f', automax=True)
m.cat_vars('lees_f', automax=True)
m.fit_mohseni('lees_f', automax=True)
m.plot_curvefit('lees_f')

######################################

class make_mohseni_hyst():
	def __init__(self, basin):
		self.basin = basin
		self.src_data = cat_d[self.basin].dropna()
		self.param_d = {}
		
	def mohseni(self, x, b, g):
		xdata = self.src_data['tavg']
		ydata = self.src_data['w_tavg']
		a = max(ydata)#.quantile(q=0.999)
		u = min(ydata)#.quantile(q=0.001)
		return u + (a-u)/(1 + np.exp(g*(b-x)))

	def fit_mohseni(self):
		xdata = self.src_data['tavg']
		ydata = self.src_data['w_tavg']
		xdata1 = self.src_data['tavg'].ix[self.src_data['month'] < 7]
		ydata1 = self.src_data['w_tavg'].ix[self.src_data['month'] < 7]
		xdata2 = self.src_data['tavg'].ix[self.src_data['month'] >= 7]
		ydata2 = self.src_data['w_tavg'].ix[self.src_data['month'] >= 7]
		b_init = 12.0
		g_init = 0.2
		popt1, pcov1 = curve_fit(self.mohseni, xdata1, ydata1, p0=[b_init, g_init])
		popt2, pcov2 = curve_fit(self.mohseni, xdata2, ydata2, p0=[b_init, g_init])
		self.param_d.update({self.basin : [popt1, popt2, pcov1, pcov2]})
		print popt1, popt2, pcov1, pcov2
	
	def plot_curvefit(self):
		xdata = self.src_data['tavg']
		ydata = self.src_data['w_tavg']
		xy = np.vstack([xdata,ydata])
		z = gaussian_kde(xy)(xy)
		xdata1 = self.src_data['tavg'].ix[self.src_data['month'] < 7]
		ydata1 = self.src_data['w_tavg'].ix[self.src_data['month'] < 7]
		xdata2 = self.src_data['tavg'].ix[self.src_data['month'] >= 7]
		ydata2 = self.src_data['w_tavg'].ix[self.src_data['month'] >= 7]
		scatter(xdata, ydata, c=z, s=100, edgecolor='')
		plot(arange(-20, 60), self.mohseni(arange(-20, 60), self.param_d[self.basin][0][0], self.param_d[self.basin][0][1]))
		plot(arange(-20, 60), self.mohseni(arange(-20, 60), self.param_d[self.basin][1][0], self.param_d[self.basin][1][1]))
