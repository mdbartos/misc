import pandas as pd
import numpy as np
import os
import ast

class get_zip_codes():

	def __init__(self, cellpath, zippath):
		self.cellpath = pd.read_csv(cellpath)
		self.zippath = pd.read_csv(zippath, sep='\t')
		self.zips = self.zippath[['ZIP', 'Lat', 'Long']]
		self.zips['Long'] = self.zips['Long'] + 360
		self.cells = [ast.literal_eval(i) for i in set(self.cellpath['latlon'])] 
		self.ll_d = {}


	def make_diff(self):
		temp_diff_d = {}
		zip_d = {}
		for i, r in self.zips.iterrows():
			zip_d.update({r['ZIP'] : None})
			fn_d = {}
			lo = tuple([r['Lat'], r['Long']])
			for fn in self.cells:
				diff = ((fn[0] - lo[0])**2 + (fn[1] - lo[1])**2)**0.5
				fn_d.update({fn : diff})
			cell = min(fn_d, key=fn_d.get)
			mi = fn_d[cell]
			zip_d[r['ZIP']] = cell		
		print zip_d.items()
		self.ll_d = zip_d

b = get_zip_codes('/home/chesterlab/Dropbox/Southwest Heat Vulnerability Team Share/EHE_days/la/historical/EHE-la_hist.csv', '/home/chesterlab/Dropbox/ASU Team Share/Zip Codes/ZipCodes_LA.csv')

b.make_diff()

ll_df = pd.DataFrame.from_dict(b.ll_d, orient='index')
ll_df['lat'] = ll_df[0]
ll_df['lon'] = ll_df[1]
del ll_df[0]
del ll_df[1]

ll_df.to_csv('la_zipcode_to_cell.csv', sep='\t')

b = get_zip_codes('/home/chesterlab/Dropbox/Southwest Heat Vulnerability Team Share/EHE_days/phx/historical/EHE-phx_hist.csv', '/home/chesterlab/Dropbox/ASU Team Share/Zip Codes/ZipCodes_Maricopa.csv')

b.make_diff()

ll_df = pd.DataFrame.from_dict(b.ll_d, orient='index')
ll_df['lat'] = ll_df[0]
ll_df['lon'] = ll_df[1]
del ll_df[0]
del ll_df[1]

ll_df.to_csv('phx_zipcode_to_cell.csv', sep='\t')
