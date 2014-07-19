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
####MAKE TEMPERATURE DB

for b in d.keys():
	get_usgs(b)

pickle.dump( temp_d, open( "basin_temps.p", "wb" ) )
