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

len_d = {}
max_d = {}

for k in temp_d.keys():
	len_d.update({k : {}})
	max_d.update({k : None})
	print k
	for i, v in temp_d[k].items():
		len_d[k].update({i : len(v)})
	if len(len_d[k]) > 0:
		maxix = max(len_d[k], key=len_d[k].get)
		maxlen = max(len_d[k].values())
		print maxix, maxlen
		max_d[k] = maxix

####################################
####GET AIR TEMP 
loc_d = {}

for fn in os.listdir('.'):
	if fn.endswith('txt'):
		f = pd.read_csv(fn, dtype={'SITE_NO' : str})
		sn = f['SITE_NO']
		f['latlon'] = zip(f['LAT_SITE'], f['LON_SITE'])
		sf = fn.split('.')[0]
		loc_d.update({sf : f[['SITE_NO', 'latlon']]})

r_latlon = pickle.load( open( "region_latlon.p", "rb"))
latlon_d = pd.concat([i for i in r_latlon.values()], ignore_index=True)
latlon_d = latlon_d.drop_duplicates()

diff_d = {}

def relate_met(basin):
	print basin
	if len(temp_d[basin]) > 0:
		diff_d.update({basin : {}})
		fn_d = {}
		ll = loc_d[basin]['latlon'].ix[loc_d[basin]['SITE_NO'] == max_d[basin]]
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
		diff_d[basin].update({max_d[basin] : cell})
	else:
		print 'no stations'

######################################

cat_d = {}

def cat_vars(basin):
	if len(diff_d[basin]) > 0:
		w = temp_d[basin][diff_d[basin].keys()[0]]
		diff_coords = diff_d[basin][diff_d[basin].keys()[0]]
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
		cat_d.update({basin : c})
	else:
		print 'No stations'
	
######################################

class make_mohseni():
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
		b_init = 12.0
		g_init = 0.2
		popt, pcov = curve_fit(self.mohseni, xdata, ydata, p0=[b_init, g_init])
		self.param_d.update({self.basin : [popt, pcov]})
		print popt
	
	def plot_curvefit(self):
		fig, ax = plt.subplots(1)
		xdata = self.src_data['tavg']
		ydata = self.src_data['w_tavg']
		xy = np.vstack([xdata, ydata])
		z = gaussian_kde(xy)(xy)
		ax.scatter(xdata, ydata, c=z, s=100, edgecolor='')
		ax.plot(arange(-20, 60), self.mohseni(arange(-20, 60), self.param_d[self.basin][0][0], self.param_d[self.basin][0][1]))
#		title('Daily Maximum Temperature at Sky Harbor Airport')
		xlabel('Air Temperature (C)')
		ylabel('Stream Temperature (C)')
#		textstr = r'$\beta=%.2f$\n$\gamma=%.2f$\n' % (self.param_d[self.basin][0][0], self.param_d[self.basin][0][1])
		textstr = '$b=%.2f$\n$g=%.2f$\n' % (self.param_d[self.basin][0][0], self.param_d[self.basin][0][1])
		props = dict(boxstyle='round', facecolor='wheat', alpha=0.5)
		ax.text(0.05, 0.95, textstr, transform=ax.transAxes, fontsize=14, verticalalignment='top', bbox=props)


for i in temp_d.keys():
	relate_met(i)
	
for g in diff_d.keys():
	cat_vars(g)

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
