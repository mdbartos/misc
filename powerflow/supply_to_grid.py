import pandas as pd
import numpy as np
from scipy import spatial

plant_860 = pd.read_excel('/home/akagi/Desktop/eia8602012/PlantY2012.xlsx', header=1)
gen_860 = pd.read_excel('/home/akagi/Desktop/eia8602012/GeneratorY2012.xlsx', sheetname='Operable', header=1)

plant_cap = pd.merge(plant_860, gen_860, on='Plant Code').groupby('Plant Code').sum()[['Summer Capacity (MW)', 'Winter Capacity (MW)', 'Nameplate Capacity (MW)']]
plant_chars = plant_860.set_index('Plant Code')[['Plant Name', 'Utility ID', 'NERC Region', 'Grid Voltage (kV)', 'Latitude', 'Longitude']]
supply_nodes = pd.concat([plant_cap, plant_chars], axis=1)

###############################
###############################
###############################

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

sub1 = trans_nodes[['s_unique', 'SUB_1']].drop_duplicates('s_unique').rename(columns={'s_unique':'node', 'SUB_1':'sub'})
sub2 = trans_nodes[['e_unique', 'SUB_2']].drop_duplicates('e_unique').rename(columns={'e_unique':'node', 'SUB_2':'sub'})
submap = pd.concat([sub1, sub2]).drop_duplicates('node').set_index('node')

###################################
###################################
###################################

tree = spatial.cKDTree(np.vstack(unique_array.values))

node_query = tree.query(supply_nodes[['Longitude', 'Latitude']].values) 

supply_to_grid = pd.concat([supply_nodes.reset_index(), submap.loc[unique_array[node_query[1]].index].reset_index()], axis=1)
