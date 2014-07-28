import numpy as np
import pandas as pd
import simplejson

f = open('Lots.json', 'r')
r = f.readlines()
j = ''.join(r)
j = j[7:-1]

d = simplejson.loads(j)

fac = {}

for i in d['Facilities']:
	fac.update({i['f_id'] : i})

df = pd.DataFrame.from_dict(fac, orient='index')
df['lat'] = [i[0] for i in df['point']]
df['lon'] = [i[1] for i in df['point']]
dfex = df[['name', 'address', 'lat', 'lon', 'building_address', 'format', 'operator', 'spaces_total', 'distance']]

dfex.to_csv('LA_parking_db_parkme.csv', encoding='utf-8')
