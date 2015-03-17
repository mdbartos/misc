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
import numpy as np
from scipy import spatial

basepath = '/home/akagi/Dropbox/NSF WSC AZ WEN Team Share/trans_and_dist'
iou = pd.read_csv('%s/iouzipcodes.csv' % basepath)
noniou = pd.read_csv('%s/noniouzipcodes.csv' % basepath)
df = pd.concat([iou, noniou])
zip1 = df.set_index('zip').loc[df.groupby('zip').size()==1].sort_index()
zipm = df.set_index('zip').loc[df.groupby('zip').size()>1].sort_index()



class quick_spatial_join():
    def __init__(self, shp1, shp2, convert_crs=0, memsize=240000000, man_input_1=None,  man_input_2=None, autorun=True, tiebreak=True):
        print 'START: %s' % (str(datetime.now()))
        print 'loading files...'        
        
        print 'getting geometry type info...'
        
        if man_input_1 ==None:
            self.man_input_1 = False
        else:
            self.man_input_1 = True
        if man_input_2 ==None:
            self.man_input_2 = False
        else:
            self.man_input_2 = True

        self.tiebreak = tiebreak

        self.shapes={'shp1':{}, 'shp2':{}}

        if man_input_1==None:
            self.shapes['shp1'].update({'file' : fiona.open(shp1, 'r')})
            self.shapes['shp1'].update({'crs': self.shapes['shp1']['file'].crs})
            self.shapes['shp1'].update({'types': self.geom_types(self.shapes['shp1']['file']).dropna()})

        else:
            self.shapes['shp1'].update({'file' : None}) 
            self.shapes['shp1'].update({'crs': man_input_1['crs']})
	    self.shapes['shp1'].update({'types': None})
            self.shapes['shp1'].update({'shp': man_input_1['shp']})
            self.shapes['shp1'].update({'poly' : None})
            self.shp1_centroids = man_input_1['shp']

        if man_input_2==None:
            self.shapes['shp2'].update({'file' : fiona.open(shp2, 'r')})
            self.shapes['shp2'].update({'crs': self.shapes['shp2']['file'].crs})
            self.shapes['shp2'].update({'types': self.geom_types(self.shapes['shp2']['file']).dropna()}) 
            self.shapes['shp2'].update({'shp' : self.homogenize_inputs('shp2', range(len(self.shapes['shp2']['file'])))})
            self.shapes['shp2'].update({'poly' : self.poly_return('shp2')})

        else:
            self.shapes['shp2'].update({'file' : None}) 
            self.shapes['shp2'].update({'crs': man_input_2['crs']})
	    self.shapes['shp2'].update({'types': man_input_2['types']})
            self.shapes['shp2'].update({'shp': man_input_2['shp']})
            self.shapes['shp2'].update({'poly' : self.poly_return('shp2')})

        self.make_kdtree()
        
        if man_input_1==None:
            shp1_size = os.path.getsize(shp1)
        else:
            shp1_size = man_input_1['shp'].values.nbytes + man_input_1['shp'].index.nbytes
        
        self.memratio = 1 + shp1_size/memsize
        
        if man_input_1==None:
            self.chunksize = len(self.shapes['shp1']['file'])/self.memratio
            self.chunks = list(self.file_chunks(range(len(self.shapes['shp1']['file'])), self.chunksize))
        else:
            self.chunksize = len(self.shapes['shp1']['shp'])/self.memratio
            self.chunks = list(self.file_chunks(range(len(self.shapes['shp1']['shp'])), self.chunksize))

        chunk_ct = 0

        self.matches = {}
        
	if autorun==True:
            for chunk_n in self.chunks:
    
                print 'Loop %s of %s...' % (chunk_ct+1, self.memratio)
                if self.shapes['shp1']['crs'] != self.shapes['shp2']['crs']:
                    if man_input_1==None:
                        self.shapes['shp1'].update({'shp' : self.convert_crs('shp1', self.shapes['shp1']['crs'], self.shapes['shp2']['crs'], chunk_n)})
                    else:
                        crs1 = Proj(self.shapes['shp1']['crs'], preserve_units=True)
                        crs2 = Proj(self.shapes['shp2']['crs'], preserve_units=True)
                        self.shp1_centroids = self.shapes['shp1']['shp'].loc[chunk_n].apply(lambda x: transform(crs1, crs2, x[0], x[1]))

                else:
                    if man_input_1==None:
                        self.shapes['shp1'].update({'shp' : self.homogenize_inputs('shp1', chunk_n)})
                
                if man_input_1==None:
                    self.shapes['shp1'].update({'poly' : self.poly_return('shp1')})
                    self.shp1_centroids = self.make_centroid()

                self.treequery = self.query_tree()
    
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
        print 'make valmap'
        valmap = self.shapes['shp2']['poly'].apply(lambda x: x.buffer(-0.001*(x.area/x.length))).apply(pd.Series).stack()
        
        valmap = valmap.mask(valmap.apply(lambda x: x.is_empty)).dropna().apply(lambda x: x.exterior.xy).apply(lambda x: np.column_stack([x[0], x[1]]))
	
        valshape = valmap.apply(lambda x: x.shape[0]).apply(lambda x: np.arange(x)).reset_index()

        print 'make idx arrays'
        idx_arrays = []

        for i in valshape.values:
            for j in i[2]:
                idx_arrays.append(np.array([i[0], i[1], i[2][j]]))

        idx_arrays=np.array(idx_arrays)

        midx = pd.MultiIndex.from_arrays([idx_arrays[:,0], idx_arrays[:,1], idx_arrays[:,2]])

        vals = np.concatenate(valmap.values)
        
        print 'make kdtree'

        self.kdtree = spatial.cKDTree(vals)
	
        self.shp2_idx = np.array(midx.get_level_values(0))

    def make_centroid(self):
        shp1_c = self.shapes['shp1']['poly'].apply(lambda x: x.centroid.coords[0])
        return shp1_c

    def query_tree(self, neighbors=1):
        print 'querying KDTree...'

        shp1_c = self.shp1_centroids
    	x_1 = shp1_c.apply(lambda x: x[0])
	y_1 = shp1_c.apply(lambda x: x[1])
	shp1_c_array = np.column_stack([x_1, y_1])
	del x_1
	del y_1

	return self.kdtree.query(shp1_c_array, k=neighbors)


    def check_matches(self):
        print 'checking predicates...'
        if self.man_input_1==False:
            s = pd.Series(self.shapes['shp1']['shp'].index, index=self.shapes['shp1']['shp'].index)
        else:
            s = pd.Series(self.shp1_centroids.index, index=self.shp1_centroids.index)
        
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
                if self.man_input_1==False:
                    n_ties['c_1'] = n_ties['index'].apply(lambda x: self.shapes['shp1']['poly'][x].centroid)
                else:
                    n_ties['c_1'] = n_ties['index'].apply(lambda x: geometry.Point(self.shp1_centroids[x]))
                n_ties['c_2'] = n_ties[0].apply(lambda x: self.shapes['shp2']['poly'][x].centroid)
                n_ties['d'] = n_ties.apply(lambda x: x['c_1'].distance(x['c_2']), axis=1)
                nontree_matches = pd.DataFrame(n_ties.groupby('index')['d'].agg(lambda x: n_ties[0].loc[x.idxmin()])).rename(columns={'d':0})  

            return pd.concat([match_d, nontree_matches]).sort_index().dropna(how='all')
            
        else:
            return match_d.sort_index().dropna(how='all')


#########################
#######################
######################

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

#trans_input = {'shp': unique_array.apply(tuple), 'crs': b.shape['crs']}
zipshp = '/home/akagi/GIS/census/cb_2013_us_zcta510_500k.shp'  

#h = quick_spatial_join(None, zipshp, man_input_1=trans_input) 
#sub_to_zip = h.matches.reset_index()
#sub_to_zip['sub'] = sub_to_zip['index'].map(submap['sub'])
#sub_to_zip['zip'] = sub_to_zip[0].astype(int).apply(lambda x: h.shapes['shp2']['file'][x]['properties']['ZCTA5CE10'])
#sub_to_zip = sub_to_zip.rename(columns={'index':'sub_id', 0:'zip_id'}).set_index('sub_id')


##### NEW APPROACH

all_vert = b.shape['shp'].apply(list).apply(pd.Series).stack().apply(tuple).reset_index()[0]
trans_input = {'shp': all_vert, 'crs': b.shape['crs']}
h = quick_spatial_join(None, zipshp, man_input_1=trans_input, memsize=4800000) 

vert_to_zip = h.matches.copy()
vert_to_zip['zip'] = vert_to_zip[0].astype(int).apply(lambda x: h.shapes['shp2']['file'][x]['properties']['ZCTA5CE10'])
vertstack = b.shape['shp'].apply(list).apply(pd.Series).stack().reset_index().rename(columns={0:'coords'}) 
vert_to_zip = pd.concat([vert_to_zip, vertstack], axis=1).reset_index()
vert_to_zip = vert_to_zip.rename(columns={'index':'vert_id', 0:'zip_id'}).set_index('vert_id')
vert_to_zip['BUS_NAME'] = vert_to_zip['level_0'].map(trans_nodes['BUS_NAME'])
vert_to_zip['x'] = vert_to_zip['coords'].apply(lambda x: x[0])
vert_to_zip['y'] = vert_to_zip['coords'].apply(lambda x: x[1])
del vert_to_zip['coords']

#trans_nodes.loc[vert_to_zip[vert_to_zip['zip']=='85210']['level_0'].unique()]
testv = vert_to_zip.loc[vert_to_zip['zip']==85210][['x', 'y']].values
v = spatial.Voronoi(testv) 
s = pd.Series(range(len(vert_to_zip.loc[vert_to_zip['zip']==85210])))
mesa = vert_to_zip.loc[vert_to_zip['zip']==85210]
iverts = s.apply(lambda x: v.vertices[v.regions[v.point_region[x]]])
iverts.index = mesa.index
mesa_verts = pd.concat([mesa, iverts], axis=1)
mesa_verts[0] = mesa_verts[0].apply(lambda x: np.vstack([x, x[0]]))
CoM = mesa_verts.groupby('BUS_NAME')['poly'].apply(lambda x: ops.cascaded_union(x)).apply(lambda x: np.column_stack(x.exterior.xy)).iloc[0]
