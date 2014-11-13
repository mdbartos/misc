import numpy as np
import pandas as pd
import os
import re
import datetime
import time

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
                for i in range(len(r)-1):
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

        df_d.update({u : df})
