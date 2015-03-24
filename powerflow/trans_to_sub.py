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

#### SPECIFY TRANSMISSION LINE SHAPEFILE

translines = '/home/akagi/Desktop/electricity_data/Transmission_Lines.shp'
translines_db = '/home/akagi/Desktop/electricity_data/Transmission_Lines.dbf'

#### CONVERT SHAPEFILE DATA INTO NUMPY ARRAYS

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
            print 'warning: coercing multilinestring to linestring'
            mlinearrays = mlinestr.apply(lambda x: np.array(list(chain(*x))))

        return pd.concat([linearrays, mlinearrays]).sort_index()    
    
    
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

#### FUNCTION FOR IMPORTING DBF FILES

def open_dbf(fn):
    dbf = ps.open(fn)
    dbpass = {col: dbf.by_col(col) for col in dbf.header}
    return_df = pd.DataFrame(dbpass)
    return return_df

#### EXTRACT STARTPOINT AND ENDPOINT OF EACH LINE

startpt = b.shape['shp'].apply(lambda x: x[0])
endpt = b.shape['shp'].apply(lambda x: x[x.shape[0]-1])

#### SPECIFY SUBSTATION SHAPEFILE

substation = '/home/akagi/Desktop/electricity_data/Substations.shp'
substation_db = '/home/akagi/Desktop/electricity_data/Substations.dbf'

ss_file = fiona.open(substation)
s_range = pd.Series(range(len(ss_file)))
ss_coords = s_range.apply(lambda x: np.array(ss_file[x]['geometry']['coordinates']))

#### CREATE KDTREE FOR NEAREST NEIGHBOR SEARCH

tree = spatial.cKDTree(np.vstack(ss_coords.values))

start_node_query = tree.query(np.vstack(startpt.values)) 
end_node_query = tree.query(np.vstack(endpt.values)) 

#### OPEN DBF FILES

trans_db = open_dbf(translines_db).rename(columns={'UNIQUE_ID':'TRANS_ID'})
sub_db = open_dbf(substation_db).rename(columns={'UNIQUE_ID':'SUB_ID'})

#### CONCATENATE DBF TO SHP

sub_cat = pd.concat([ss_coords, sub_db], axis=1)

#### RESULTS 

start = sub_db.iloc[start_node_query[1]].rename(columns={'SUB_ID':'SUB_1_ID', 'NAME':'NAME_1'})
end = sub_db.iloc[end_node_query[1]].rename(columns={'SUB_ID':'SUB_2_ID', 'NAME':'NAME_2'})

crosswalk = pd.concat([trans_db, start[['NAME_1', 'SUB_1_ID']].reset_index(), end[['NAME_2', 'SUB_2_ID']].reset_index()], axis=1)

crosswalk['ERR_1'] = start_node_query[0]
crosswalk['ERR_2'] = end_node_query[0]

#### CHECK RESULTS

#note that names sometimes differ between files
crosswalk[~(crosswalk['SUB_1'] == crosswalk['NAME_1'])][['SUB_1', 'NAME_1']]
#1000 non-matches
crosswalk[~(crosswalk['SUB_2'] == crosswalk['NAME_2'])][['SUB_2', 'NAME_2']]
#~40 non-matches

#### RETURN RESULTS 

crosswalk[['TRANS_ID', 'SUB_1_ID', 'SUB_2_ID', 'ERR_1', 'ERR_2', 'NAME_1', 'SUB_1', 'NAME_2', 'SUB_2']]
