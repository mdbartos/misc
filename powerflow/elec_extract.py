import fiona
import numpy as np
import pandas as pd
import pysal as ps
from scipy import spatial
from shapely import geometry
from shapely import ops

tnodes = fiona.open('/home/akagi/GIS/elecnodes.shp', 'r')  

s = pd.Series(range(len(tnodes)))
s = s.apply(lambda x: tnodes[x]['geometry']['coordinates'])

sname = pd.Series(range(len(tnodes)))
sname = sname.apply(lambda x: tnodes[x]['properties']['BUS_NAME'])

###DROP UNDETERMINED

s = s.drop(sname[sname.str.contains('Undetermined')].index).reset_index(drop=True)
sname = sname[~sname.str.contains('Undetermined')].reset_index(drop=True)

#### MAKE VORONOI POLYGONS

x = s.apply(lambda x: x[0])
y = s.apply(lambda x: x[1])

nodearray = np.column_stack([x, y])

vn = spatial.Voronoi(nodearray)

### APPLY VORONOI TO DIFFERENT UTILITIES

srp = pd.Series(np.array(sname[sname=='Salt River Project'].index))  

srp_poly = ops.cascaded_union(srp.apply(lambda x: geometry.Polygon(vn.vertices[vn.regions[vn.point_region[x]]])).values)


for i in range(len(srp_poly.boundary)):
    fill(srp_poly.boundary[i].xy[0], srp_poly.boundary[i].xy[1], color='blue')


aps = pd.Series(np.array(sname[sname=='Arizona Public Service Co'].index))  

aps_poly = ops.cascaded_union(aps.apply(lambda x: geometry.Polygon(vn.vertices[vn.regions[vn.point_region[x]]])).values)

for i in range(len(aps_poly.boundary)):
    fill(aps_poly.boundary[i].xy[0], aps_poly.boundary[i].xy[1], color='red')

tep = pd.Series(np.array(sname[sname=='Tucson Electric Power Co'].index))  

tep_poly = ops.cascaded_union(tep.apply(lambda x: geometry.Polygon(vn.vertices[vn.regions[vn.point_region[x]]])).values)

for i in range(len(tep_poly.boundary)):
    fill(tep_poly.boundary[i].xy[0], tep_poly.boundary[i].xy[1], color='green')

navopache = pd.Series(np.array(sname[sname=='Navopache Electric Co-op'].index))  

navopache_poly = ops.cascaded_union(navopache.apply(lambda x: geometry.Polygon(vn.vertices[vn.regions[vn.point_region[x]]])).values)

for i in range(len(navopache_poly.boundary)):
    fill(navopache_poly.boundary[i].xy[0], navopache_poly.boundary[i].xy[1], color='orange')

mohave = pd.Series(np.array(sname[sname=='Mohave Electric CO-OP, Inc.'].index))  

mohave_poly = ops.cascaded_union(mohave.apply(lambda x: geometry.Polygon(vn.vertices[vn.regions[vn.point_region[x]]])).values)

for i in range(len(mohave_poly.boundary)):
    fill(mohave_poly.boundary[i].xy[0], mohave_poly.boundary[i].xy[1], color='brown')


#### STATES

states = fiona.open('/home/akagi/GIS/census/cb_2013_us_state_500k/cb_2013_us_state_500k.shp', 'r')

az = np.array(states[0]['geometry']['coordinates'][0])

fill(az[:,0], az[:,1], color='0.60')

##### URBAN AREAS

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
        plot(c[:,0], c[:,1], color='black')


##### COUNTIES

county = fiona.open('/home/akagi/GIS/census/cb_2013_us_county_500k/cb_2013_us_county_500k.shp')

ct = pd.Series(range(len(county)))

ct_st = ct.apply(lambda x: county[x]['properties']['STATEFP'])

az_ct = ct_st[ct_st=='04']

for i in az_ct.index:
    for r in range(len(county[i]['geometry']['coordinates'])):
        if len(county[i]['geometry']['coordinates']) > 1:
            c = np.array(county[i]['geometry']['coordinates'][r][0])
        else:
            c = np.array(county[i]['geometry']['coordinates'][0])
        plot(c[:,0], c[:,1], color='0.3')

