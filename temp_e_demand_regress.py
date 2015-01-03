import numpy as np
import pandas as pd
import os
import re
import datetime
import time
from scipy.stats import gaussian_kde

basepath = '/home/akagi/Documents/wecc_form_714'

path_d = {
1993: '93WSCC1/WSCC',
1994: '94WSCC1/WSCC1994',
1995: '95WSCC1',
1996: '96WSCC1/WSCC1996',
1997: '97wscc1',
1998: '98WSCC1/WSCC1',
1999: '99WSCC1/WSCC1',
2000: '00WSCC1/WSCC1',
2001: '01WECC/WECC01/wecc01',
2002: 'WECCONE3/WECC One/WECC2002',
2003: 'WECC/WECC/WECC ONE/wecc03',
2004: 'WECC_2004/WECC/WECC One/ferc',
2006: 'form714-database_2006_2013/form714-database/Part 3 Schedule 2 - Planning Area Hourly Demand.csv'
}

util = {
'aps' : 803,
'srp' : 16572,
'ldwp' : 11208
        }

df_path_d = {}

def build_paths():
    for y in path_d.keys():
        if y < 2006:
            pathstr = basepath + '/' + path_d[y]
            dirstr = ' '.join(os.listdir(pathstr))
#            print dirstr
            for u in util.keys():
                if not u in df_path_d:
                    df_path_d.update({u : {}})
                srcstr = '%s\d\d.dat' % (u)
 #               print srcstr
                match = re.search(srcstr, dirstr, re.I)
#                print type(match.group())
                rpath = pathstr + '/' + match.group()
                df_path_d[u].update({y : rpath})
        elif y == 2006:
            pathstr = basepath + '/' + path_d[y]
            for u in util.keys():
                if not u in df_path_d:
                    df_path_d.update({u : {}})
                df_path_d[u].update({y : pathstr})

df_d = {}

def build_df():
    for u in df_path_d.keys():
        df = pd.DataFrame()
        for y in df_path_d[u].keys():
            if y < 2006:
                print df_path_d[u][y]
                f = open(df_path_d[u][y])
                r = f.readlines()
                r = [g.replace('\t', '      ') for g in r if len(g) > 70]
                for i in range(0, len(r)-1, 2):
                    entry = [r[i], r[i+1]]
                    mo = int(r[i][:2])
                    day = int(r[i][2:4])
                    yr = r[i][4:6]
                    if yr[0] == '0':
                        yr = int('20' + yr)
                    else:
                        yr = int('19' + yr)

                    am = [int(j) for j in entry[0][20:].split()]
                    pm = [int(j) for j in entry[1][20:].split()]
                    ampm = am + pm
                    entry_df = pd.DataFrame()
                    dt_ix = pd.date_range(start=datetime.datetime(yr, mo, day, 0), end=datetime.datetime(yr, mo, day, 23), freq='H')
                    entry_df['load'] = ampm
#                    print entry_df
                    entry_df.index = dt_ix
                    df = df.append(entry_df)
#                    print entry_df
            elif y == 2006:
                pass
        
	df['year'] = [i.year for i in df.index]
        df_d.update({u : df})



build_paths()
build_df()



#### Import census data

az_census = pd.read_csv('/home/akagi/Dropbox/NSF WSC AZ WEN Team Share/trans_and_dist/az_census.csv', index_col=0).T
az_census.index = az_census.index.astype(int)

ca_census = pd.read_csv('/home/akagi/Dropbox/NSF WSC AZ WEN Team Share/trans_and_dist/ca_census.csv', index_col=0).T
ca_census.index = ca_census.index.astype(int)

#### Regress by year for each utility

#### SRP

srp_regress = pd.concat([az_census['Maricopa'], df_d['srp'].groupby('year').mean()], axis=1, join='inner')

a, b = np.polyfit(srp_regress['Maricopa'], srp_regress['load'], 1)
y, p = np.polyfit(range(len(srp_regress)), srp_regress['Maricopa'], 1)
df_d['srp']['pop_est'] = [((y/(365*24))*x + p) for x in range(len(df_d['srp']))]
df_d['srp']['load_trend'] = df_d['srp']['pop_est'].apply(lambda x: a*x + b)
df_d['srp']['load_detrend'] = df_d['srp']['load'] - df_d['srp']['load_trend']

#### APS

aps_regress = pd.concat([az_census.sum(axis=1), df_d['aps'].groupby('year').mean()], axis=1, join='inner')

a2, b2 = np.polyfit(aps_regress[0], aps_regress['load'], 1)
y2, p2 = np.polyfit(range(len(aps_regress)), aps_regress[0], 1)
df_d['aps']['pop_est'] = [((y2/(365*24))*x + p2) for x in range(len(df_d['aps']))]
df_d['aps']['load_trend'] = df_d['aps']['pop_est'].apply(lambda x: a2*x + b2)
df_d['aps']['load_detrend'] = df_d['aps']['load'] - df_d['aps']['load_trend']

#### LDWP

ldwp_regress = pd.concat([ca_census['LosAngeles'], df_d['ldwp'].groupby('year').mean()], axis=1, join='inner')

a3, b3 = np.polyfit(ldwp_regress['LosAngeles'], ldwp_regress['load'], 1)
y3, p3 = np.polyfit(range(len(ldwp_regress)), ldwp_regress['LosAngeles'], 1)
df_d['ldwp']['pop_est'] = [((y3/(365*24))*x + p3) for x in range(len(df_d['ldwp']))]
df_d['ldwp']['load_trend'] = df_d['ldwp']['pop_est'].apply(lambda x: a3*x + b3)
df_d['ldwp']['load_detrend'] = df_d['ldwp']['load'] - df_d['ldwp']['load_trend']


def plot_curvefit(xdata, ydata):
    xy = np.vstack([xdata,ydata])
    z = gaussian_kde(xy)(xy)
    scatter(xdata, ydata, c=z, s=100, edgecolor='')


###################

#### SCRAPS

laciv = pd.read_csv('/home/akagi/Desktop/laciv.csv', index_col=0)
laciv.index = pd.to_datetime(laciv.index)

df = pd.DataFrame(index=pd.date_range(start=datetime.date(1961,1,1), end=datetime.date(2014,2,25), freq='H'))

tmax = pd.DataFrame(laciv['tmax']).set_index(pd.Series([datetime.datetime(i.year, i.month, i.day, 12) for i in laciv['tmax'].index])).rename(columns={'tmax':'temp'})

tmin = pd.DataFrame(laciv['tmin']).set_index(pd.Series([datetime.datetime(i.year, i.month, i.day, 0) for i in laciv['tmin'].index])).rename(columns={'tmin':'temp'})
 
tmaxmin = pd.concat([tmax, tmin])
trange = pd.concat([df, tmaxmin], axis=1)
trange['temp'] = trange['temp'].interpolate('time')
trange['temp'].loc[trange['temp'] < -100] = np.nan

normtemp = (trange['temp'] - trange['temp'].mean()) / (trange['temp'].max() - trange['temp'].min())
cat = pd.concat([df_d['ldwp'], normtemp], axis=1, join='inner')
cat['date'] = cat.index
summercat = cat.loc[cat['date'].apply(lambda x: x.month).isin([6,7,8])]

#### SRP

phxsh = pd.read_csv('/home/akagi/Desktop/sha_hist.csv')

phxsh['date'] = phxsh['DATE'].apply(lambda x: datetime.datetime.strptime(str(x), '%Y%m%d'))

phxsh = phxsh.set_index('date')

phxsh['tmax'] = phxsh['TMAX'].apply(lambda x: float(str(x)[:-1] + '.' + str(x)[-1]))

phxsh['tmin'] = phxsh['TMIN'].apply(lambda x: float(str(x)[:-1] + '.' + str(x)[-1]))

df = pd.DataFrame(index=pd.date_range(start=datetime.date(1961,1,1), end=datetime.date(2014,2,25), freq='H'))

tmax = pd.DataFrame(phxsh['tmax']).set_index(pd.Series([datetime.datetime(i.year, i.month, i.day, 12) for i in phxsh['tmax'].index])).rename(columns={'tmax':'temp'})

tmin = pd.DataFrame(phxsh['tmin']).set_index(pd.Series([datetime.datetime(i.year, i.month, i.day, 0) for i in phxsh['tmin'].index])).rename(columns={'tmin':'temp'})
 
tmaxmin = pd.concat([tmax, tmin])
trange = pd.concat([df, tmaxmin], axis=1)
trange['temp'] = trange['temp'].interpolate('time')
trange['temp'].loc[trange['temp'] < -100] = np.nan

normtemp = (trange['temp'] - trange['temp'].mean()) / (trange['temp'].max() - trange['temp'].min())
cat = pd.concat([df_d['srp'], normtemp], axis=1, join='inner')
cat['date'] = cat.index

cat['year'] = [i.year for i in cat['date']]
cat['month'] = [i.month for i in cat['date']]
cat['day'] = [i.day for i in cat['date']]

summercat = cat.loc[cat['date'].apply(lambda x: x.month).isin([6,7,8])]

#########
g = summercat.groupby(['year', 'month', 'day']).max().reset_index()
scatter(g['temp'], g['load_detrend'], c=g['year'])

#y, p = np.polyfit(srp_regress.index, srp_regress['Maricopa'], 1)
#srp_regress.index = pd.Series(srp_regress.index).apply(lambda x: datetime.datetime(x, 6, 1, 0))
#tcat = pd.concat([df_d['srp'], srp_regress['Maricopa']], axis=1)
