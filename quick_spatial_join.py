import pandas as pd
import numpy as np
import fiona
from shapely import geometry
from shapely import ops
from itertools import chain

states = fiona.open('/home/akagi/GIS/census/cb_2013_us_state_500k/cb_2013_us_state_500k.shp', 'r')

county = fiona.open('/home/akagi/GIS/census/cb_2013_us_county_500k/cb_2013_us_county_500k.shp', 'r')

book400 = fiona.open('/home/akagi/GIS/2014_All_Parcel_Shapefiles/2014_Book400.shp', 'r')

zipcodes = fiona.open('/home/akagi/Desktop/census_az/Arizona_ZIP_Codes.shp', 'r') 

class quick_spatial_join():
    def __init__(self, shp1, shp2):
        
        self.shapes = {
                        'shp1' : {
                            'shp': self.poly_vectorize(shp1),
                            'types' : self.geom_types(shp1)
                            },
                
                        'shp2': {
                            'shp': self.poly_vectorize(shp2),
                            'types' : self.geom_types(shp2)
                            }
                }
        
        self.shapes['shp1'].update({'poly' : self.poly_return('shp1')})
        self.shapes['shp2'].update({'poly' : self.poly_return('shp2')})
      
        
    def poly_vectorize(self, shpfile):
        s = pd.Series(range(len(shpfile)))
        return s.apply(lambda x: shpfile[x]['geometry']['coordinates'])
      
    def poly_len(self, shpfile):
        s = pd.Series(range(len(shpfile)))
        return s.apply(lambda x: len(shpfile[x]['geometry']['coordinates']))
    
    def poly_return(self, shp):
        
        poly_df = pd.Series(index=self.shapes[shp]['shp'].index)
        
        p = self.shapes[shp]['shp'].loc[self.shapes[shp]['types']=='Polygon'].apply(lambda x: geometry.Polygon(x[0]))
        poly_df.loc[p.index] = p
        
        mp = self.shapes[shp]['shp'].loc[self.shapes[shp]['types']== 'MultiPolygon'].apply(lambda x: pd.Series(list(chain(*x))))
        for i in mp.index:
            poly_df.loc[i] = ops.cascaded_union(mp.loc[i].dropna().apply(lambda x: geometry.Polygon(x)))
        return poly_df
            
    def geom_types(self, shp):
        s = pd.Series(range(len(shp)))
        return s.apply(lambda x: shp[x]['geometry']['type'])
    
    def pt_in_bounds(self, x_coord, y_coord, shp_bounds):
        return list(shp_bounds.loc[(shp_bounds['xmin'] < x_coord) & (shp_bounds['ymin'] < y_coord) & (shp_bounds['xmax'] > x_coord) & (shp_bounds['ymax'] > y_coord)].index)
    
    def centroid_in_poly(self, shp1, shp2):
        shp1_c = self.shapes[shp1]['poly'].apply(lambda x: pd.Series(x.centroid.coords[0])).rename(columns={0:'x', 1:'y'})
        shp2_bounds = self.shapes[shp2]['poly'].apply(lambda x: pd.Series(x.bounds)).rename(columns={0:'xmin', 1:'ymin', 2:'xmax', 3:'ymax'})
        c_memb = shp1_c.apply(lambda x: self.pt_in_bounds(x['x'], x['y'], shp2_bounds), axis=1).apply(pd.Series)
        c_memb.columns = [str(i) for i in c_memb.columns]
        geom = self.shapes['shp2']['types']
        ct_c = shp1_c.apply(geometry.Point, axis=1)
    
        def points_in_poly():
      
            ct_c = shp1_c.apply(geometry.Point, axis=1)
      
            c_poly = c_memb.where(c_memb.apply(lambda x: x.map(geom) == 'Polygon')).dropna(how='all').dropna(axis=1, how='all').stack().astype(int).reset_index().set_index(0).sort_index()['level_0'].reset_index()        
      
            bool_df = pd.Series()
      
            for i in pd.Series(c_poly[0]).astype(int).unique():
                m = self.shapes[shp2]['poly'].loc[i]
                bool_df = pd.concat([bool_df, c_poly.loc[c_poly[0] == i, 'level_0'].apply(lambda x: m.contains(ct_c.loc[x]))])
      
            return c_poly[bool_df].set_index('level_0')
      
      
        def points_in_mpoly():
      
            c_mpoly = c_memb.where(c_memb.apply(lambda x: x.map(geom) == 'MultiPolygon')).dropna(how='all').dropna(axis=1, how='all').stack().astype(int).reset_index().set_index(0).sort_index()['level_0'].reset_index()        
      
            bool_df = pd.Series()
      
            for i in pd.Series(c_mpoly[0]).astype(int).unique():
                m = self.shapes[shp2]['poly'].loc[i]
                bool_df = pd.concat([bool_df, c_mpoly.loc[c_mpoly[0] == i, 'level_0'].apply(lambda x: m.contains(ct_c.loc[x]))])
      
            return c_mpoly[bool_df].set_index('level_0')
      
        return_df = pd.concat([pd.DataFrame(points_in_poly()), points_in_mpoly()]).sort_index().reindex(range(len(self.shapes[shp1]['shp'])))
        return_df.index.rename('shape1', inplace=True)
        return_df.rename(columns={0:'shape2'}, inplace=True)
      
        return return_df

