import pandas as pd
import numpy as np
import fiona
from shapely import geometry
from shapely import ops
from itertools import chain
from pyproj import Proj, transform
from scipy import spatial
from matplotlib import path
import os
from datetime import datetime
import sys
import pysal as ps


translines = '/home/akagi/GIS/Energy/HSIP_2010_ElectricTransmissionLines.shp'

class vectorize_lines():
    def __init__(self, shp):
        print 'START: %s' % (str(datetime.now()))
        print 'loading files...'        
        self.shape = {
                            'file' : fiona.open(shp, 'r')     
                }
        
        print 'getting geometry type info...'

        self.shape.update({'crs': self.shape['file'].crs})
        self.shape.update({'types': self.geom_types(self.shape['file']).dropna()})

        self.shape.update({'shp' : self.homogenize_inputs()})
        
    def homogenize_inputs(self):
        print 'homogenizing inputs...'
        
        linev = self.line_extract(self.shape['file']).dropna()
        gtypes = self.shape['types'].loc[linev.index]

        linestr = linev.loc[gtypes=='LineString'] 
        mlinestr = linev.loc[gtypes=='MultiLineString'] 

#        a_mpoly = mpoly.apply(lambda x: list(chain(*x)))
        
        #### HOMOGENIZE LINESTR

        if len(linestr) > 0:
            linearrays = linestr.apply(lambda x: np.array(x))

        #### HOMOGENIZE MULTILINESTR
        
        if len(mlinestr) > 0:
            pass

        return linearrays  
    
    
    def line_extract(self, shpfile):
        s = pd.Series(range(len(shpfile)))
        
        def return_coords(x):
            try:
                return shpfile[x]['geometry']['coordinates']
            except:
                return np.nan
            
        return s.apply(return_coords)
      
            
    def geom_types(self, shp):
        s = pd.Series(range(len(shp)))
        def return_geom(x):
            try:
                return shp[x]['geometry']['type']
            except:
                return np.nan
        return s.apply(return_geom)

b = vectorize_lines(translines)

startpt = b.shape['shp'].apply(lambda x: x[0])
endpt = b.shape['shp'].apply(lambda x: x[x.shape[0]-1])

####################

startsplit = startpt.apply(pd.Series).rename(columns = {0: 's_x', 1: 's_y'}) 
endsplit = endpt.apply(pd.Series).rename(columns = {0: 'e_x', 1: 'e_y'}) 

#unique_x = pd.Series(pd.concat([startsplit['s_x'], endsplit['e_x']]).unique())
#unique_y = pd.Series(pd.concat([startsplit['s_x'], endsplit['e_x']]).unique())

startstr = startsplit['s_x'].astype(str).str.strip() + ' ' + startsplit['s_y'].astype(str).str.strip()
endstr = endsplit['e_x'].astype(str).str.strip() + ' ' + endsplit['e_y'].astype(str).str.strip()
uniquenode = pd.concat([startstr, endstr]).unique()
uniquemap = pd.Series(range(len(uniquenode)), index=uniquenode)

start_unique = startstr.map(uniquemap)
end_unique = endstr.map(uniquemap)

start = pd.concat([startsplit, start_unique], axis=1).rename(columns={0:'s_unique'})
end = pd.concat([endsplit, end_unique], axis=1).rename(columns={0:'e_unique'})

fn = '/home/akagi/GIS/Energy/HSIP_2010_ElectricTransmissionLines.dbf'
dbf = ps.open(fn)
dbpass = {col: dbf.by_col(col) for col in dbf.header}
df = pd.DataFrame(dbpass)


trans_nodes = pd.concat([start['s_unique'], end['e_unique'], df[['BUS_NAME', 'TOT_CAP_KV', 'SUB_1', 'SUB_2']]], axis=1)

unique_array = pd.Series(uniquenode).str.split().apply(lambda x: np.array([np.float64(x[0]), np.float64(x[1])]))

###### VORONOI POLYGONS #######

s = pd.Series(range(len(unique_array)))

vn = spatial.Voronoi(np.vstack(unique_array.values))

paths = s.apply(lambda x: vn.vertices[vn.regions[vn.point_region[x]]])

paths_closed = paths.apply(lambda x: np.vstack([x, x[0]]))

az_indexes = np.unique(trans_nodes[trans_nodes['BUS_NAME'].isin(['Salt River Project', 'Arizona Public Service Co', 'Tucson Electric Power Co'])][['s_unique', 'e_unique']].values.ravel()) 

srp_indexes = np.unique(trans_nodes[trans_nodes['BUS_NAME']=='Salt River Project'][['s_unique', 'e_unique']].values.ravel()) 

aps_indexes = np.unique(trans_nodes[trans_nodes['BUS_NAME']=='Arizona Public Service Co'][['s_unique', 'e_unique']].values.ravel()) 

tep_indexes = np.unique(trans_nodes[trans_nodes['BUS_NAME']=='Tucson Electric Power Co'][['s_unique', 'e_unique']].values.ravel()) 

for i in paths_closed.loc[aps_indexes].values:
    plot(i[:,0], i[:,1], c='blue', label='aps')
for i in paths_closed.loc[srp_indexes].values:
    plot(i[:,0], i[:,1], c='red', label='srp')
for i in paths_closed.loc[tep_indexes].values:
    plot(i[:,0], i[:,1], c='green', label='tep')

for i in paths_closed.loc[az_indexes].values:
    plot(i[:,0], i[:,1])

states = fiona.open('/home/akagi/GIS/census/cb_2013_us_state_500k/cb_2013_us_state_500k.shp', 'r')

az = np.array(states[0]['geometry']['coordinates'][0])

fill(az[:,0], az[:,1], color='0.60')

ua = fiona.open('/home/akagi/GIS/census/cb_2013_us_ua10_500k/cb_2013_us_ua10_500k.shp', 'r')

ua_s = pd.Series(range(len(ua)))
ua_city = ua_s.apply(lambda x: ua[x]['properties']['NAME10'])
ua_state = ua_city.str.extract(', *([A-Z][A-Z])')
az_city = ua_city[ua_state=='AZ'] 

for i in az_city.index:
    for r in range(len(ua[i]['geometry']['coordinates'])):
        if len(ua[i]['geometry']['coordinates']) > 1:
            c = np.array(ua[i]['geometry']['coordinates'][r][0])
        else:
            c = np.array(ua[i]['geometry']['coordinates'][0])
        fill(c[:,0], c[:,1], color='0.30', linewidth=0)

###### D3 JS NODES #######

fn = '/home/akagi/GIS/Energy/HSIP_2010_ElectricTransmissionLines.dbf'
dbf = ps.open(fn)
dbpass = {col: dbf.by_col(col) for col in dbf.header}
df = pd.DataFrame(dbpass)

trans_nodes = pd.concat([start['s_unique'], end['e_unique'], df[['BUS_NAME', 'TOT_CAP_KV', 'SUB_1', 'SUB_2']]], axis=1)

s_names = trans_nodes[['s_unique', 'SUB_1']].rename(columns = {'SUB_1': 'name'}).set_index('s_unique')
e_names = trans_nodes[['e_unique', 'SUB_2']].rename(columns = {'SUB_2': 'name'}).set_index('e_unique')

#### CHECK IF SUBSTATION NAMES ARE UNIQUE
g1 = pd.concat([s_names, e_names])
#g1.reset_index().groupby('index').apply(lambda x: len(x['SUB'].unique())).max()
#### YUP

#### CHECK IF UTILITY NAMES ARE UNIQUE
s_names = trans_nodes[['s_unique', 'BUS_NAME']].set_index('s_unique')
e_names = trans_nodes[['e_unique', 'BUS_NAME']].set_index('e_unique')
g = pd.concat([s_names, e_names]).reset_index().groupby('index')
#g.apply(lambda x: len(x['BUS_NAME'].unique())).max()
#### NOPE
### GET MOST COMMON UTILITY FOR EACH

utils = g.agg(lambda x: x.value_counts().index[0]).rename(columns={'BUS_NAME': 'group'}) 

utils['name'] = pd.Series(utils.index).map(g1['name'].drop_duplicates()).fillna('Unknown')

az_utils = utils[utils['group'].isin(['Salt River Project', 'Arizona Public Service Co', 'Tucson Electric Power Co'])][['name', 'group']].dropna() 

az_nodes = trans_nodes[trans_nodes['BUS_NAME'].isin(['Salt River Project', 'Arizona Public Service Co', 'Tucson Electric Power Co'])].dropna() 

intmap = pd.Series(range(len(az_utils.index)), index=az_utils.index)

az_nodes['s_unique'] = az_nodes['s_unique'].map(intmap)
az_nodes['e_unique'] = az_nodes['e_unique'].map(intmap)


azlinks = az_nodes[['s_unique', 'e_unique', 'TOT_CAP_KV']].rename(columns={'s_unique':'source', 'e_unique':'target', 'TOT_CAP_KV':'value'}).dropna()

az_utils = az_utils.reset_index()[['name', 'group']]
nodes_json = az_utils.to_json(orient='records')
links_json = azlinks.to_json(orient='records')

json_str = '{"nodes" : ' + nodes_json + ',' + '"links" : ' + links_json + '}'
########

links = trans_nodes[['s_unique', 'e_unique', 'TOT_CAP_KV']].rename(columns={'s_unique':'source', 'e_unique':'target', 'TOT_CAP_KV':'value'})

nodes = trans_nodes[['s_unique', 'e_unique', 'TOT_CAP_KV']].rename(columns={'s_unique':'source', 'e_unique':'target', 'TOT_CAP_KV':'value'})

