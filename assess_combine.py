import os
import numpy as np
import pandas as pd

basepath = '/home/akagi/Desktop/assessor'

#### GET SUPP DATA

master = pd.read_csv('%s/assessor_2014.csv' % (basepath))

head = open('%s/supp_2014/st42076dat_Heading.txt' % basepath).readlines()[0].split('|')

mc = pd.DataFrame()

for fn in os.listdir('%s/supp_2014' % (basepath)):
    if fn.endswith('dat'):
        df = pd.read_csv('%s/supp_2014/%s' % (basepath, fn), sep='|', names=head)
        for c in df.columns:
            if df[c].dtype == object:
                df[c] = df[c].str.replace('(\s+)$', '')
        mc = mc.append(df)

books = pd.DataFrame()

for i in [100, 200, 300, 400, 500]:
    df = pd.read_csv('%s/book%s.txt' % (basepath, i))
    books = books.append(df)

books = books.drop_duplicates(subset=['APN'])

mc_full = pd.concat([mc.set_index('PARCEL_NUM'), books.set_index('APN')], axis=1, join='inner')
