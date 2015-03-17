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
import pysal

class quick_spatial_join():
    def __init__(self, shp1, shp2, convert_crs=0, memsize=240000000, man_input=None, autorun=True, tiebreak=True):
        print 'START: %s' % (str(datetime.now()))
        print 'loading files...'        
        
        print 'getting geometry type info...'

        self.tiebreak = tiebreak

        if man_input==None:

            self.shapes = {
                            'shp1' : {
                                'file' : fiona.open(shp1, 'r')
                                },
                    
                            'shp2': {
                                'file' : fiona.open(shp2, 'r')
                                }
                    }

            self.shapes['shp1'].update({'crs': self.shapes['shp1']['file'].crs})
            self.shapes['shp1'].update({'types': self.geom_types(self.shapes['shp1']['file']).dropna()})
            self.shapes['shp2'].update({'crs': self.shapes['shp2']['file'].crs})
            self.shapes['shp2'].update({'types': self.geom_types(self.shapes['shp2']['file']).dropna()})
    
            self.shapes['shp2'].update({'shp' : self.homogenize_inputs('shp2', range(len(self.shapes['shp2']['file'])))})
            self.shapes['shp2'].update({'poly' : self.poly_return('shp2')})

        else:

            self.shapes = {
                            'shp1' : {
                                'file' : fiona.open(shp1, 'r')
                                },
                    
                            'shp2': {
                                'file' : None
                                }
                    }

            self.shapes['shp1'].update({'crs': self.shapes['shp1']['file'].crs})
            self.shapes['shp1'].update({'types': self.geom_types(self.shapes['shp1']['file']).dropna()})
            self.shapes['shp2'].update({'crs': man_input['crs']})
	    self.shapes['shp2'].update({'types': man_input['types']})
            self.shapes['shp2'].update({'shp': man_input['shp']})
            self.shapes['shp2'].update({'poly' : self.poly_return('shp2')})

        self.make_kdtree()

        self.memratio = 1 + os.path.getsize(shp1)/memsize
        self.chunksize = len(self.shapes['shp1']['file'])/self.memratio
        self.chunks = list(self.file_chunks(range(len(self.shapes['shp1']['file'])), self.chunksize))

        chunk_ct = 0

        self.matches = {}
        
	if autorun==True:
            for chunk_n in self.chunks:
    
                print 'Loop %s of %s...' % (chunk_ct+1, self.memratio)
                if self.shapes['shp1']['crs'] != self.shapes['shp2']['crs']:
                    self.shapes['shp1'].update({'shp' : self.convert_crs('shp1', self.shapes['shp1']['crs'], self.shapes['shp2']['crs'], chunk_n)})
                else:
                    self.shapes['shp1'].update({'shp' : self.homogenize_inputs('shp1', chunk_n)})
                
                self.shapes['shp1'].update({'poly' : self.poly_return('shp1')})
    
                self.shp1_centroids, self.treequery = self.query_tree()
    
                self.matches[chunk_ct] = self.check_matches()
    
                chunk_ct = chunk_ct + 1
    
            if len(self.matches)>1:
    		self.matches = pd.concat([i for i in self.matches.values()])
    	    elif len(self.matches)==1:
    		self.matches = self.matches[0]
    
            print 'END: %s' % (str(datetime.now()))


    def file_chunks(self, l, n):
        """ Yield successive n-sized chunks from l.
        """
        for i in xrange(0, len(l), n):
            yield np.array(l[i:i+n])
        
    def homogenize_inputs(self, shp, chunk):
        print 'homogenizing inputs for %s...' % (shp)
        
        d = {}
        
        bv = self.poly_vectorize(self.shapes[shp]['file'], chunk).dropna()
        gtypes = self.shapes[shp]['types'].loc[bv.index]

        poly = bv.loc[gtypes=='Polygon'] 
        mpoly = bv.loc[gtypes=='MultiPolygon'] 

        apoly = poly.apply(lambda x: list(chain(*x)))
        a_mpoly = mpoly.apply(lambda x: list(chain(*x)))
        
        #### HOMOGENIZE POLYGONS

        if len(poly) > 0:
            polyarrays = pd.Series(apoly.apply(lambda x: np.array(x)))
            p_x_arrays = polyarrays.apply(lambda x: np.array(x)[:,0])
            p_y_arrays = polyarrays.apply(lambda x: np.array(x)[:,1])
            p_trans_arrays = pd.concat([p_x_arrays, p_y_arrays], axis=1)

            d['p_geom'] = pd.Series(zip(p_trans_arrays[0], p_trans_arrays[1]), index=p_trans_arrays.index).apply(np.column_stack)
            d['p_geom'] = d['p_geom'][d['p_geom'].apply(lambda x: x.shape[0]>=4)]

        #### HOMOGENIZE MULTIPOLYGONS
        
        if len(mpoly) > 0:            
            mpolydims = a_mpoly.apply(lambda x: np.array(x).ndim)

            ##ndim==1

            if (mpolydims==1).any():
                m_x_arrays_1 = a_mpoly[mpolydims==1].apply(pd.Series).stack().apply(lambda x: np.array(x)[:,0])
                m_y_arrays_1 = a_mpoly[mpolydims==1].apply(pd.Series).stack().apply(lambda x: np.array(x)[:,1])

                mp = pd.concat([m_x_arrays_1, m_y_arrays_1], axis=1)

                m_geom_1_s = pd.Series(zip(mp[0], mp[1])).apply(np.column_stack)

                empty_s = pd.Series(range(len(mp)), index=mp.index)
                empty_s = empty_s.reset_index()
                empty_s[0] = m_geom_1_s
                empty_s = empty_s[empty_s[0].apply(lambda x: x.shape[0]>=4)]

                d['m_geom_1'] = empty_s.groupby('level_0').apply(lambda x: tuple(list(x[0])))

            ##ndim==3

            if (mpolydims==3).any():
                m_arrays_3 = a_mpoly[mpolydims==3].apply(pd.Series).stack().apply(lambda x: np.array(x)[:,[0,1]])
                m_arrays_3 = m_arrays_3[m_arrays_3.apply(lambda x: x.shape[0]>=4)]

                d['m_geom_3'] = m_arrays_3.reset_index().groupby('level_0').apply(lambda x: tuple(list(x[0])))
        
        returndf = pd.concat(d.values()).sort_index()
        return returndf

        
    def convert_crs(self, shp, crsfrom, crsto, chunk):
        print 'converting coordinate reference system of %s...' % (shp)
        
        crsfrom = Proj(crsfrom, preserve_units=True)
        crsto = Proj(crsto, preserve_units=True)
        
        d = {}
        
        bv = self.poly_vectorize(self.shapes[shp]['file'], chunk).dropna()
        gtypes = self.shapes[shp]['types'].loc[bv.index]

        poly = bv.loc[gtypes=='Polygon'] 
        mpoly = bv.loc[gtypes=='MultiPolygon'] 

        apoly = poly.apply(lambda x: list(chain(*x)))
        a_mpoly = mpoly.apply(lambda x: list(chain(*x)))
        
        #### CONVERT POLYGONS
        
        if len(poly) > 0:
            polyarrays = pd.Series(apoly.apply(lambda x: np.array(x)))
            p_x_arrays = polyarrays.apply(lambda x: np.array(x)[:,0])
            p_y_arrays = polyarrays.apply(lambda x: np.array(x)[:,1])
            p_trans_arrays = pd.concat([p_x_arrays, p_y_arrays], axis=1).apply(lambda x: transform(crsfrom, crsto, x[0], x[1]), axis=1)
        
            d['p_trans_geom'] = p_trans_arrays.apply(np.array).apply(np.column_stack)
            d['p_trans_geom'] = d['p_trans_geom'][d['p_trans_geom'].apply(lambda x: x.shape[0]>=4)]
        
        #### CONVERT MULTIPOLYGONS
        
        if len(mpoly) > 0:
            mpolydims = a_mpoly.apply(lambda x: np.array(x).ndim)
        
            ##ndim==1
            
            if (mpolydims==1).any():
                m_x_arrays_1 = a_mpoly[mpolydims==1].apply(pd.Series).stack().apply(lambda x: np.array(x)[:,0])
                m_y_arrays_1 = a_mpoly[mpolydims==1].apply(pd.Series).stack().apply(lambda x: np.array(x)[:,1])
                mp = pd.concat([m_x_arrays_1, m_y_arrays_1], axis=1)
                m_x_flat_arrays_1 = pd.Series([j[:,0] for j in [np.column_stack(i) for i in np.column_stack([mp[0].values, mp[1].values])]])
                m_y_flat_arrays_1 = pd.Series([j[:,0] for j in [np.column_stack(i) for i in np.column_stack([mp[0].values, mp[1].values])]])
                m_trans_arrays_1 = pd.concat([m_x_flat_arrays_1, m_y_flat_arrays_1], axis=1).apply(lambda x: transform(crsfrom, crsto, x[0], x[1]), axis=1)
                m_trans_geom_1_s = m_trans_arrays_1.apply(np.array).apply(np.column_stack)
                empty_s = pd.Series(range(len(mp)), index=mp.index).reset_index()
                empty_s[0] = m_trans_geom_1_s
                empty_s = empty_s[empty_s[0].apply(lambda x: x.shape[0]>=4)]

                d['m_trans_geom_1'] = empty_s.groupby('level_0').apply(lambda x: tuple(list(x[0])))
        
            ##ndim==3
            if (mpolydims==3).any():
                m_trans_arrays_3 = a_mpoly[mpolydims==3].apply(pd.Series).stack().apply(lambda x: np.array(x)[:,[0,1]]).apply(lambda x: transform(crsfrom, crsto, x[:,0], x[:,1]))

                m_trans_geom_3 = m_trans_arrays_3.apply(np.array).apply(np.column_stack)
                m_trans_geom_3 = m_trans_geom_3[m_trans_geom_3.apply(lambda x: x.shape[0]>=4)]
                m_trans_geom_3_u = m_trans_geom_3.unstack()

                d['m_trans_geom_3'] = pd.Series(zip(m_trans_geom_3_u[0], m_trans_geom_3_u[1]), index=m_trans_geom_3_u.index)
        
        return pd.concat(d.values()).sort_index()
    
    
    def poly_vectorize(self, shpfile, chunk):
        s = pd.Series(chunk, index=chunk)
        
        def return_coords(x):
            try:
                return shpfile[x]['geometry']['coordinates']
            except:
                return np.nan
            
        return s.apply(return_coords)
    
    def handle_topo_err(self, k):
        if k.is_valid:
            return k
        else:
            return k.boundary.convex_hull
   
    def handle_empty(self, k):
        if k.is_empty:
            return np.nan
        elif type(k) != geometry.polygon.Polygon:
            return np.nan
        else:
            return k

    def try_union(self, k):
        try:
    	    return ops.cascaded_union(k)
        except:
            try:
    	        u = k[0]
    	        for z in range(len(k))[1:]:
    	            u = u.union(k[z])
    	        return u
            except:
                return geometry.Polygon(np.vstack(pd.Series(k).apply(lambda x: x.boundary.coords).apply(np.array))).convex_hull

    def poly_return(self, shp):
        print 'creating polygons for %s...' % (shp)
        poly_df = pd.Series(index=self.shapes[shp]['shp'].index)

        geomtypes = self.shapes[shp]['types'].loc[poly_df.index]
        
#        print 'making p'
        if (geomtypes=='Polygon').any():
            p = self.shapes[shp]['shp'].loc[geomtypes=='Polygon'].apply(lambda x: geometry.Polygon(x))#.apply(self.handle_empty) 
    #        print 'setting polydf with p'
            poly_df.loc[p.index] = p.copy()
        
#        print 'making mp'
        if (geomtypes=='MultiPolygon').any():
            mp = self.shapes[shp]['shp'].loc[geomtypes == 'MultiPolygon'].apply(lambda x: (pd.Series(list(x)))).stack().apply(geometry.Polygon)
	    
	    if mp.apply(lambda x: not x.is_valid).any():
	        mp = mp.apply(self.handle_topo_err).apply(self.handle_empty).dropna()
		
	    mp = mp.reset_index().groupby('level_0').apply(lambda x: list(x[0])).apply(self.try_union)
            
    #        print 'setting poly df with mp'
            poly_df.loc[mp.index] = mp.copy()

#        print 'making nullgeom'
        nullgeom = poly_df[poly_df.isnull()].index

#        print 'dropping nullgeom from polydf'
        poly_df = poly_df.drop(nullgeom)
        
#        print 'dropping nullgeom from selp.shapes.shp'
        self.shapes[shp]['shp'] = self.shapes[shp]['shp'].drop(nullgeom)
        
        return poly_df
            
    def geom_types(self, shp):
        s = pd.Series(range(len(shp)))
        def return_geom(x):
            try:
                return shp[x]['geometry']['type']
            except:
                return np.nan
        return s.apply(return_geom)
      
    def make_kdtree(self):
        print 'constructing KDTree...'
        valmap = self.shapes['shp2']['poly'].apply(lambda x: x.buffer(-0.001*(x.area/x.length))).apply(pd.Series).stack().apply(lambda x: x.exterior.xy).apply(lambda x: np.column_stack([x[0], x[1]]))
	
        valshape = valmap.apply(lambda x: x.shape[0]).apply(lambda x: np.arange(x)).reset_index()

        idx_arrays = []

        for i in valshape.values:
            for j in i[2]:
                idx_arrays.append(np.array([i[0], i[1], i[2][j]]))

        idx_arrays=np.array(idx_arrays)

        midx = pd.MultiIndex.from_arrays([idx_arrays[:,0], idx_arrays[:,1], idx_arrays[:,2]])

        vals = np.concatenate(valmap.values)

        self.kdtree = spatial.cKDTree(vals)
	
        self.shp2_idx = np.array(midx.get_level_values(0))

    def query_tree(self, neighbors=1):
        print 'querying KDTree...'

        shp1_c = self.shapes['shp1']['poly'].apply(lambda x: x.centroid.coords[0])
    	x_1 = shp1_c.apply(lambda x: x[0])
	y_1 = shp1_c.apply(lambda x: x[1])
	shp1_c_array = np.column_stack([x_1, y_1])
	del x_1
	del y_1

	return shp1_c, self.kdtree.query(shp1_c_array, k=neighbors)


    def check_matches(self):
        print 'checking predicates...'
        s = pd.Series(self.shapes['shp1']['shp'].index, index=self.shapes['shp1']['shp'].index)

        geom = self.shapes['shp2']['types']
        ct_c = self.shp1_centroids.apply(geometry.Point)

	match_d = {}

	if self.treequery[1].ndim == 1:
            containing_p = self.shapes['shp2']['poly'].loc[self.shp2_idx[self.treequery[1]]].reset_index()
            containing_p.index = s.values
	    containing_bool = s.apply(lambda x: containing_p.loc[x, 0].contains(ct_c[x]))
	    match_d.update({0 : containing_p['index'].where(containing_bool)})
             
        else:
	    for i in range(self.treequery[1].shape[1]):
                containing_p = self.shapes['shp2']['poly'].loc[self.shp2_idx[self.treequery[1][:,i]]].reset_index()
                containing_p.index = s.values                 
	        containing_bool = s.apply(lambda x: containing_p.loc[x, 0].contains(ct_c[x]))
	        match_d.update({i : containing_p['index'].where(containing_bool)})

        match_d = pd.DataFrame.from_dict(match_d)
        print len(match_d.dropna())

        print 'matching polygons not captured by KDtree...'

        nullidx = match_d[match_d.isnull().all(axis=1)].index

	if (self.shapes['shp2']['types']=='Polygon').any():
            poly = self.shapes['shp2']['shp'].loc[self.shapes['shp2']['types']=='Polygon']

	if (self.shapes['shp2']['types']=='MultiPolygon').any():
            mpoly = self.shapes['shp2']['shp'].loc[self.shapes['shp2']['types']== 'MultiPolygon'].apply(lambda x: (pd.Series(list(x)))).stack()
        
	if (self.shapes['shp2']['types']=='Polygon').any() and (self.shapes['shp2']['types']=='MultiPolygon').any():  
	    p_midx = pd.MultiIndex.from_arrays([np.array(poly.index), np.zeros(len(poly.index))])
            poly.index = p_midx
            poly_all = pd.concat([poly, mpoly])
	elif (self.shapes['shp2']['types']=='Polygon').any() and not (self.shapes['shp2']['types']=='MultiPolygon').any():
	        p_midx = pd.MultiIndex.from_arrays([np.array(poly.index), np.zeros(len(poly.index))])
                poly.index = p_midx
		poly_all = poly
	elif (self.shapes['shp2']['types']=='MultiPolygon').any() and not (self.shapes['shp2']['types']=='Polygon').any():
		poly_all = mpoly

        polypath = poly_all.apply(lambda x: path.Path(x))

        shp1_c = self.shp1_centroids.loc[nullidx]
        x_1 = shp1_c.apply(lambda x: x[0])
        y_1 = shp1_c.apply(lambda x: x[1])
        c = np.column_stack([x_1, y_1])
        shp1_c_map = pd.Series(shp1_c.index)

        poly_result = polypath.apply(lambda x: x.contains_points(c))
        if poly_result.apply(lambda x: x.any()).any():
            poly_result = poly_result[poly_result.apply(lambda x: x.any())].apply(lambda x: np.where(x)[0]).apply(lambda x: shp1_c_map[x]).stack()

            nontree_matches = pd.DataFrame(poly_result.index.get_level_values(0), index=poly_result.values)

	    if self.tiebreak==True:
                n_ties = nontree_matches.reset_index()
                n_ties['c_1'] = n_ties['index'].apply(lambda x: self.shapes['shp1']['poly'][x].centroid)
                n_ties['c_2'] = n_ties[0].apply(lambda x: self.shapes['shp2']['poly'][x].centroid)
                n_ties['d'] = n_ties.apply(lambda x: x['c_1'].distance(x['c_2']), axis=1)
                nontree_matches = pd.DataFrame(n_ties.groupby('index')['d'].agg(lambda x: n_ties[0].loc[x.idxmin()])).rename(columns={'d':0})  

            return pd.concat([match_d, nontree_matches]).sort_index().dropna(how='all')
            
        else:
            return match_d.sort_index().dropna(how='all')




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


translines = '/home/akagi/GIS/Energy/HSIP_2010_ElectricTransmissionLines.shp'

#fn = '/home/akagi/GIS/Energy/HSIP_2010_ElectricTransmissionLines.dbf'
#dbf = ps.open(fn)
#dbpass = {col: dbf.by_col(col) for col in dbf.header}
#df = pd.DataFrame(dbpass)

####### GET VORONOI OF TRANSLINES #####

b = vectorize_lines(translines)

startpt = b.shape['shp'].apply(lambda x: x[0])
endpt = b.shape['shp'].apply(lambda x: x[x.shape[0]-1])

startsplit = startpt.apply(pd.Series).rename(columns = {0: 's_x', 1: 's_y'}) 
endsplit = endpt.apply(pd.Series).rename(columns = {0: 'e_x', 1: 'e_y'}) 

startstr = startsplit['s_x'].astype(str).str.strip() + ' ' + startsplit['s_y'].astype(str).str.strip()
endstr = endsplit['e_x'].astype(str).str.strip() + ' ' + endsplit['e_y'].astype(str).str.strip()

uniquenode = pd.concat([startstr, endstr]).unique()
uniquemap = pd.Series(range(len(uniquenode)), index=uniquenode)

start_unique = startstr.map(uniquemap)
end_unique = endstr.map(uniquemap)

start = pd.concat([startsplit, start_unique], axis=1).rename(columns={0:'s_unique'})
end = pd.concat([endsplit, end_unique], axis=1).rename(columns={0:'e_unique'})

#trans_nodes = pd.concat([start['s_unique'], end['e_unique'], df[['BUS_NAME', 'TOT_CAP_KV', 'SUB_1', 'SUB_2']]], axis=1)

unique_array = pd.Series(uniquenode).str.split().apply(lambda x: np.array([np.float64(x[0]), np.float64(x[1])]))

s = pd.Series(range(len(unique_array)))

vn = spatial.Voronoi(np.vstack(unique_array.values))

paths = s.apply(lambda x: vn.vertices[vn.regions[vn.point_region[x]]])

paths_closed = paths.apply(lambda x: np.vstack([x, x[0]]))

ptypes = pd.Series('Polygon', index=paths_closed.index)

f = fiona.open(translines, 'r')
shp2_crs = f.crs
f.close()

#################

trans_input = {'shp': paths_closed, 'types':ptypes, 'crs': shp2_crs}

books = {'book100' : '/home/akagi/GIS/2014_All_Parcel_Shapefiles/2014_Book100.shp', 'book200': '/home/akagi/GIS/2014_All_Parcel_Shapefiles/2014_Book200.shp', 'book300': '/home/akagi/GIS/2014_All_Parcel_Shapefiles/2014_Book300.shp', 'book400': '/home/akagi/GIS/2014_All_Parcel_Shapefiles/2014_Book400.shp', 'book500': '/home/akagi/GIS/2014_All_Parcel_Shapefiles/2014_Book500.shp'}

for m in books.keys():
    h = quick_spatial_join(books[m], None, man_input=trans_input)
    h.matches.to_csv('%s.csv' % (m))

####DEBUGGING

h = quick_spatial_join(books['book300'], None, man_input=trans_input, autorun=False)

shp1_arr = h.convert_crs('shp1', h.shapes['shp1']['crs'], h.shapes['shp2']['crs'], np.arange(len(h.shapes['shp1']['file'])))

multipoly = shp1_arr[h.shapes['shp1']['types']=='MultiPolygon']

stack_m = multipoly.apply(lambda x: (pd.Series(list(x)))).stack()

plists = stack_m.apply(geometry.Polygon).apply(h.handle_topo_err).apply(h.handle_empty).dropna().reset_index().groupby('level_0').apply(lambda x: list(x[0]))

def try_union(k):
    try:
	return ops.cascaded_union(k)
    except:
        try:
	    u = k[0]
	    for z in range(len(k))[1:]:
	        u = u.union(k[z])
	    return u
        except:
            return geometry.Polygon(np.vstack(pd.Series(k).apply(lambda x: x.boundary.coords).apply(np.array))).convex_hull

###############

for m in books.keys():
    h = quick_spatial_join(books[m], None, man_input=trans_input)
    h.matches.to_csv('%s.csv' % (books[m]))

h = quick_spatial_join(book100, None, man_input=trans_input)
book100_matches = h.matches

h = quick_spatial_join(book400, None, man_input=trans_input)
book400_matches = h.matches

#la = '/home/tabris/Desktop/Vulnerability Files/parcels_AIN_2.shp'
#latracts = '/home/tabris/Desktop/Vulnerability Files/tl_2010_06037_tract10.shp'

#b = quick_spatial_join(la, latracts, memsize=400000000)
#b = quick_spatial_join(la, latracts)


def check_matches():
    print 'checking predicates...'
    s = pd.Series(h.shapes['shp1']['shp'].index, index=h.shapes['shp1']['shp'].index)

    geom = h.shapes['shp2']['types']
    ct_c = h.shp1_centroids.apply(geometry.Point)

    match_d = {}

    if h.treequery[1].ndim == 1:
        containing_p = h.shapes['shp2']['poly'].loc[h.shp2_idx[h.treequery[1]]].reset_index()
        containing_p.index = s.values
	containing_bool = s.apply(lambda x: containing_p.loc[x, 0].contains(ct_c[x]))
	match_d.update({0 : containing_p['index'].where(containing_bool)})
             
    else:
	for i in range(h.treequery[1].shape[1]):
            containing_p = h.shapes['shp2']['poly'].loc[h.shp2_idx[h.treequery[1][:,i]]].reset_index()
            containing_p.index = s.values                 
	    containing_bool = s.apply(lambda x: containing_p.loc[x, 0].contains(ct_c[x]))
	    match_d.update({i : containing_p['index'].where(containing_bool)})

    match_d = pd.DataFrame.from_dict(match_d)
    print len(match_d.dropna())

    print 'matching polygons not captured by KDtree...'

    nullidx = match_d[match_d.isnull().all(axis=1)].index

    return match_d, nullidx

def get_stragglers(match_d, nullidx):
	if (h.shapes['shp2']['types']=='Polygon').any():
            poly = h.shapes['shp2']['shp'].loc[h.shapes['shp2']['types']=='Polygon']

	if (h.shapes['shp2']['types']=='MultiPolygon').any():
            mpoly = h.shapes['shp2']['shp'].loc[h.shapes['shp2']['types']== 'MultiPolygon'].apply(lambda x: (pd.Series(list(x)))).stack()
        
	if (h.shapes['shp2']['types']=='Polygon').any() and (h.shapes['shp2']['types']=='MultiPolygon').any():  
	    p_midx = pd.MultiIndex.from_arrays([np.array(poly.index), np.zeros(len(poly.index))])
            poly.index = p_midx
            poly_all = pd.concat([poly, mpoly])
	elif (h.shapes['shp2']['types']=='Polygon').any() and not (h.shapes['shp2']['types']=='MultiPolygon').any():
	        p_midx = pd.MultiIndex.from_arrays([np.array(poly.index), np.zeros(len(poly.index))])
                poly.index = p_midx
		poly_all = poly
	elif (h.shapes['shp2']['types']=='MultiPolygon').any() and not (h.shapes['shp2']['types']=='Polygon').any():
		poly_all = mpoly

        polypath = poly_all.apply(lambda x: path.Path(x))

        shp1_c = h.shp1_centroids.loc[nullidx]
        x_1 = shp1_c.apply(lambda x: x[0])
        y_1 = shp1_c.apply(lambda x: x[1])
        c = np.column_stack([x_1, y_1])
        shp1_c_map = pd.Series(shp1_c.index)

        poly_result = polypath.apply(lambda x: x.contains_points(c))
        if poly_result.apply(lambda x: x.any()).any():
            poly_result = poly_result[poly_result.apply(lambda x: x.any())].apply(lambda x: np.where(x)[0]).apply(lambda x: shp1_c_map[x]).stack()

            nontree_matches = pd.DataFrame(poly_result.index.get_level_values(0), index=poly_result.values)
        
	return nontree_matches

#
#            return pd.concat([match_d, nontree_matches]).sort_index().dropna(how='all')
#            
#        else:
#            return match_d.sort_index().dropna(how='all')



#### TIEBREAK

n_ties = nontree.reset_index()
n_ties['c_1'] = n_ties['index'].apply(lambda x: h.shapes['shp1']['poly'][x].centroid)
n_ties['c_2'] = n_ties[0].apply(lambda x: h.shapes['shp2']['poly'][x].centroid)
n_ties['d'] = n_ties.apply(lambda x: x['c_1'].distance(x['c_2']), axis=1)
n_ties.groupby('index')['d'].agg(lambda x: n_ties[0].loc[x.idxmin()])
