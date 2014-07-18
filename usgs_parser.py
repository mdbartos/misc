import os
import pandas as pd
import numpy as np
import urllib2 as url
from StringIO import StringIO
import pickle
from datetime import date
from datetime import timedelta as td
import ast

d = {}
src_str = ""

for fn in os.listdir('.'):
	if fn.endswith('txt'):
		f = pd.read_csv(fn, dtype={'SITE_NO' : str})
		sn = f['SITE_NO']
		sf = fn.split('.')[0]
		d.update({sf : sn})

temp_d = {}
		
def get_usgs(basin):
	temp_d.update({basin : {}})
	for i in d[basin]:
		string_op = ("http://waterdata.usgs.gov/nwis/dv?referred_module=sw&search_site_no=%s" % (i))
		string_ed = "&search_site_no_match_type=exact&site_tp_cd=OC&site_tp_cd=OC-CO&site_tp_cd=ES&site_tp_cd=LK&site_tp_cd=ST&site_tp_cd=ST-CA&site_tp_cd=ST-DCH&site_tp_cd=ST-TS&index_pmcode_00010=1&group_key=NONE&sitefile_output_format=html_table&column_name=agency_cd&column_name=site_no&column_name=station_nm&range_selection=date_range&begin_date=1900-01-01&end_date=2014-07-15&format=rdb&date_format=YYYY-MM-DD&rdb_compression=value&list_of_search_criteria=search_site_no%2Csite_tp_cd%2Crealtime_parameter_selection"
		conn_str = string_op + string_ed
		conn = url.urlopen(conn_str)
		r = conn.readlines()
		if len(r) < 10:
			print "no data"
			continue
		else:
			st_i = None
			for x, line in enumerate(r):
				if "No sites" in line[0]:
					print "No sites found in %s" % (x)
					break
				elif 'agency_cd' in line:
					st_i = x
			
			if st_i != None:
				raw_li = r[st_i:]
				raw_str = ''.join(raw_li)
				st_input = StringIO(raw_str)
				t = pd.read_table(st_input)
				t = t[1:]
				print t
				temp_d[basin].update({i : t})
		
##################################
####RELOAD TEMPERATURE DB

for b in d.keys():
	get_usgs(b)

pickle.dump( temp_d, open( "basin_temps.p", "wb" ) )

##################################
####FIND GAUGE WITH GREATEST NUMBER OF ENTRIES

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

######################################

def cat_vars(basin):
	w = temp_d[basin][diff_d[basin].keys()[0]]
	diff_coords = diff_d[basin][diff_d[basin].keys()[0]]
#	print diff_coords
#	print [i for i in t['datetime']]
	w['date'] = [(date(int(i.split('-')[0]), int(i.split('-')[1]), int(i.split('-')[2]))) for i in w['datetime']]
	w['w_tmax'] = w['01_00010_00001']
	w['w_tmin'] = w['01_00010_00002']
	w = w[['date', 'site_no','w_tmax', 'w_tmin']]
	w = w.set_index('date')
	w = w.replace(to_replace=['Ice'], value=[0.0])
	w['w_tmax'] = [float(i) for i in w['w_tmax']]
	w['w_tmin'] = [float(i) for i in w['w_tmin']]
	w['w_tavg'] = 0.5*(w['w_tmin'] + w['w_tmax'])
	print w
	print w.index
	print w['w_tmax'].quantile(q=0.95)
	print w['w_tmax'].quantile(q=0.05)
	print max(w['w_tmax'])
	print min(w['w_tmin'])
	print max(w['w_tmin'])
	a = pd.read_csv('./master/data_%s_%s' % (str(diff_coords[0]), str(diff_coords[1])))
	d1 = date(1949, 1, 1)
	d2 = date(2010, 12, 31)
	ddelta = d2 - d1
	dr = [d1 + td(days=i) for i in range(ddelta.days + 1)]
	print len(dr)
	a['date'] = dr
	a = a.set_index['date']
	c = pd.concat([w,c], axis=1)
		
######################################
####OLD

#diff_d = {}
#
#def relate_met(basin):
#	diff_d.update({basin : {}})
#	for i in temp_d[basin].keys():
#		fn_d = {}
#		ll = loc_d[basin]['latlon'].ix[loc_d[basin]['SITE_NO'] == i]
#		ll = tuple(ll.values)[0]
#		lat = ll[0]
#		lon = ll[1]
#		for v in latlon_d.values:
#			diff = ((v[0] - lat)**2 + (v[1] - lon)**2)**0.5
#			fn_d.update({v : diff})
#		cell = min(fn_d, key=fn_d.get)
#		print cell
#		mi = fn_d[cell]
#		print mi
#		diff_d[basin].update({i : cell})


###################################









##################################


testtab = url.urlopen("http://waterdata.usgs.gov/nwis/dv?referred_module=sw&search_site_no=13343000&search_site_no_match_type=exact&site_tp_cd=OC&site_tp_cd=OC-CO&site_tp_cd=ES&site_tp_cd=LK&site_tp_cd=ST&site_tp_cd=ST-CA&site_tp_cd=ST-DCH&site_tp_cd=ST-TS&dv_count_nu=1&index_pmcode_00010=1&group_key=NONE&sitefile_output_format=html_table&column_name=agency_cd&column_name=site_no&column_name=station_nm&range_selection=days&period=365&begin_date=2013-07-16&end_date=2014-07-15&format=rdb&date_format=YYYY-MM-DD&rdb_compression=value&list_of_search_criteria=search_site_no%2Csite_tp_cd%2Cobs_count_nu%2Crealtime_parameter_selection")

r = testtab.readlines()
st_i = None

for i, line in enumerate(r):
	if "No sites" in line[0]:
		break
	elif 'agency_cd' in line:
		st_i = i
		
raw_li = r[st_i:]
raw_str = ''.join(raw_li)
st_input = StringIO(raw_str)
t = pd.read_table(st_input)
t = t[1:]
print t
