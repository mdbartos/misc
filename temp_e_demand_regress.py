import numpy as np
import pandas as pd
import os
import re

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
                srcstr = '%s\d\d' % (u)
 #               print srcstr
                match = re.search(srcstr, dirstr, re.I)
                print type(match.group())
                rpath = pathstr + '/' + match.group()
        elif y == 2006:
            pathstr = basepath + '/' + path_d[y]
