import os
import pandas as pd
import numpy as np
from fuzzywuzzy import fuzz
from fuzzywuzzy import process

#match flags: z: zip, n: street number, d: direction, s: street name, t: street type


assessor_path = '/home/akagi/Desktop/assessor' 

df = pd.read_csv('%s/mc_assessor.txt' % (assessor_path), sep='\t')
df_sub = df[['OADDRESS1', 'OADDRESS2', 'OCITY', 'OSTATE', 'APN', 'SITUSADD', 'SSUITE', 'SCITY', 'SZIP', 'SUBDIVISIO']]
#df_sub.to_csv('mc_sub', sep='\t')
df_sub = df_sub.dropna(subset=['SITUSADD'])

abbrv = pd.read_csv('%s/usps_abbrv.csv' % (assessor_path), header=None)
abbrv[1] = abbrv[1].str.replace('[^A-Z]', '')
abbrv[0] = abbrv[0].str.replace(' ', '')
abbrv.loc[abbrv[0] == 'WAY', 1] = 'WY'

abbrv_li = list(abbrv[1])
additions = ['HAVEN', 'GLEN', 'GLENN', 'WAY', 'TR', 'PT', 'POINT', 'HW', 'LP', 'PW', 'PZ', 'COURT', 'GAP', 'HOLLOW', 'STR', 'CROSSING', 'PLACE', 'PKY', 'ALLEY', 'AVENUE', 'BOULEVARD', 'DRIVE', 'ROAD', 'FREEWAY', 'HIGHWAY', 'LANE', 'PARKWAY', 'WALK', 'CENTER', 'CIRCLE', 'STREET'] 
abbrv_li.extend(additions)
abbrv_str = '| '.join(abbrv_li)

#### MANUALLY GET NONSTANDARD POSTAL ABBREVIATIONS

#lensplit = lambda x: len(x.split())
#df_sub['SPLITLEN'] = df_sub['SITUSADD'].apply(lensplit)
#threesplit = df_sub['SITUSADD'].loc[df_sub['SPLITLEN'] <= 3]
#foursplit = df_sub['SITUSADD'].loc[df_sub['SPLITLEN'] > 3]

#threesplit.str.extract('([A-Z]*)$').unique()
#foursplit.str.extract('([A-Z]*)$').unique()

#### TYPE 1
#type1 = df_sub['SITUSADD'].str.extract('(\d*) *(N\.?|S\.?|E\.?|W\.?) *([A-Z,0-9, ]*) *( ST| DR| PL| LN| WY| RD| AVE| CT| BLVD| CIR| FWY| TER| MALL| TR| PASS| PKWY)')

type1 = df_sub['SITUSADD'].str.extract("(\d*) *(N\.?|S\.?|E\.?|W\.?) +([A-Z,0-9, ,-,',\.]*) *( %s)$" % (abbrv_str))

nontype1 = df_sub.loc[~df_sub['SITUSADD'].str.contains("(\d*) *(N\.?|S\.?|E\.?|W\.?) +([A-Z,0-9, ,-,',\.]*) *( %s)$" % (abbrv_str))]

type2 = nontype1['SITUSADD'].loc[nontype1['SITUSADD'].str.contains(" [N\.?|W\.?|S\.?|E\.?] ")].str.extract("(\d*) *(N\.?|S\.?|E\.?|W\.?) +([A-Z,0-9, ,-,',\.]*)$")

type3 = nontype1['SITUSADD'].loc[~nontype1['SITUSADD'].str.contains(" [N\.?|W\.?|S\.?|E\.?] ")].str.extract("(\d*) *([A-Z,0-9, ,-,',\.]*)( %s)$" % (abbrv_str))

type1_names = pd.DataFrame(type1.dropna()[[0,1,2,3]]).rename(columns={0:'SNUM', 1:'DIR', 2:'STREET', 3:'STYPE'})
type2_names = pd.DataFrame(type2.dropna()[[0,2]]).rename(columns={0:'SNUM',1:'DIR', 2:'STREET'})
 
type3_names = pd.DataFrame(type3.dropna()[[0,1]]).rename(columns={0:'SNUM', 1:'STREET', 2:'STYPE'})
 

street_loc = pd.concat([type1_names, type2_names, type3_names], axis=0)
street_names = street_loc['STREET']
street_names = street_names.drop(street_names[street_names.str.len() == 1].index)
street_names = street_names.drop(street_names[street_names.isin(['RD', 'PL', 'LP', 'DR', 'HWY', 'OLD', 'VIS'])].index)

streetsort = pd.DataFrame(street_names.unique())
streetsort['len'] = streetsort[0].str.len()
streetsort_str = '|'.join(streetsort.sort('len', ascending=False)[0].values)

df_sub = pd.concat([df_sub, street_loc], axis=1)
df_sub['STYPE'] = df_sub['STYPE'].str.replace(' ', '')

#####################

#READ MCDPH DEATH DATA

mcdph_path = '/home/akagi/Desktop/MCDPH_data/csv'

death = pd.read_csv('%s/DeathAddress.csv' % (mcdph_path), index_col=0).dropna().rename(columns={'DRESZIP':'SZIP'})

#morb = pd.read_csv('%s/HDDAddress.csv' % (mcdph_path), index_col=0).dropna()

death['DRESADDRES'] = death['DRESADDRES'].str.upper().str.replace('.', '').str.replace(',', '')

df_dd = df_sub.drop_duplicates(subset=['SITUSADD'])[['SITUSADD', 'APN', 'SNUM', 'DIR', 'STREET', 'STYPE', 'SZIP']]

df_dd['SITUSADD'] = df_dd['SITUSADD'].str.replace('.', '').str.replace(',', '')

df_dd['STYPE'] = df_dd['STYPE'].map(pd.Series(abbrv.set_index(0)[1])).fillna(df_dd['STYPE'])

#### TRY TO GET A BETTER REGEX CAPTURE

death_wf_2 = death['DRESADDRES'].str.extract('(\d*) *(N|W|E|S|NORTH|WEST|EAST|SOUTH) *(%s) *(%s)' % (streetsort_str, abbrv_str)).dropna()

death_add_2 = death_wf_2[0] + ' ' + death_wf_2[1] + ' ' + death_wf_2[2] + death_wf_2[3]

death_df_2 = pd.DataFrame(death_add_2, columns=['SITUSADD'])
death_df_2['FID'] = death_df_2.index
death_df_2 = pd.concat([death_df_2, death['SZIP']], axis=1, join='inner')

#### FIRST PASS--EXTRANEOUS INFORMATION (APT, BLDG, etc.)

firstpass = pd.merge(death_df_2, df_dd, on='SITUSADD', how='inner', suffixes=['_MCDPH', '_ASSESS']).drop_duplicates(subset=['FID'])

comp_firstpass = death_df_2.loc[~death_df_2.index.isin(firstpass['FID'])]

comp_firstpass['SNUM'] = comp_firstpass['SITUSADD'].str.extract('(\d*) *(N|W|E|S|NORTH|WEST|EAST|SOUTH) *(%s) *(%s)' % (streetsort_str, abbrv_str))[0]

comp_firstpass['DIR'] = comp_firstpass['SITUSADD'].str.extract('(\d*) *(N|W|E|S|NORTH|WEST|EAST|SOUTH) *(%s) *(%s)' % (streetsort_str, abbrv_str))[1].str.replace('NORTH','N').str.replace('SOUTH','S').str.replace('WEST','W').str.replace('EAST','E') 

comp_firstpass['STREET'] = comp_firstpass['SITUSADD'].str.extract('(\d*) *(N|W|E|S|NORTH|WEST|EAST|SOUTH) *(%s) *(%s)' % (streetsort_str, abbrv_str))[2]

comp_firstpass['STYPE'] = comp_firstpass['SITUSADD'].str.extract('(\d*) *(N|W|E|S|NORTH|WEST|EAST|SOUTH) *(%s) *(%s)' % (streetsort_str, abbrv_str))[3].str.replace(' ', '')

comp_firstpass['STYPE'] = comp_firstpass['STYPE'].map(pd.Series(abbrv.set_index(0)[1])).fillna(comp_firstpass['STYPE'])


#### SECOND PASS--DIFFERENT CARDINAL DIRECTION

secondpass = pd.merge(comp_firstpass, df_dd, on=['SNUM', 'DIR', 'STREET', 'STYPE'], how='inner', suffixes=['_MCDPH', '_ASSESS']).drop_duplicates(subset=['FID'])

comp_secondpass = comp_firstpass[~comp_firstpass.index.isin(secondpass['FID'])]

#### THIRD PASS--NON-MATCHING STREET NUMBER

test = pd.merge(comp_secondpass[comp_secondpass['SNUM'] != ''], df_dd[df_dd['SNUM'] != ''], on=['DIR', 'STREET', 'STYPE', 'SZIP'], suffixes=['_MCDPH', '_ASSESS']).set_index('FID').reset_index()

test['SNUM_DIFF'] = (test['SNUM_MCDPH'].astype(int) - test['SNUM_ASSESS'].astype(int))  

test['SNUM_ABS'] = (test['SNUM_MCDPH'].astype(int) - test['SNUM_ASSESS'].astype(int)).apply(lambda x: abs(x))

thirdpass = pd.DataFrame(columns=test.columns)

for i in test['FID'].unique():
    t = test[test['FID'] == i]
    lo = t[t['SNUM_DIFF'] < 0]
    hi = t[t['SNUM_DIFF'] > 0]

    if len(lo) > 0:
        ixmin_lo = lo['SNUM_ABS'].idxmin()
        thirdpass = thirdpass.append(t.loc[ixmin_lo])

    if len(hi) > 0:
        ixmin_hi = hi['SNUM_ABS'].idxmin()
        thirdpass = thirdpass.append(t.loc[ixmin_hi])

comp_thirdpass = comp_secondpass[~comp_secondpass.index.isin(thirdpass['FID'].unique())]

#### FOURTH PASS--NON-MATCHING DIRECTION

fourthpass = pd.merge(comp_thirdpass[comp_thirdpass['SNUM'] != ''], df_dd[df_dd['SNUM'] != ''], on=['SNUM', 'STREET', 'STYPE', 'SZIP'], suffixes=['_MCDPH', '_ASSESS'])

comp_fourthpass = comp_thirdpass[~comp_thirdpass.index.isin(fourthpass['FID'].unique())]

#### FIFTH PASS--NON-MATCHING STREET TYPE

fifthpass = pd.merge(comp_fourthpass[comp_fourthpass['SNUM'] != ''], df_dd[df_dd['SNUM'] != ''], on=['SNUM', 'STREET', 'DIR', 'SZIP'], suffixes=['_MCDPH', '_ASSESS'])


#### NON WELL-FORMED/MISSPELLED/MISSING STREET

non_wf = death.loc[~death.index.isin(death_df_2.index)]
non_wf = non_wf.loc[~(non_wf['DRESADDRES'] == 'UNKNOWN')]
non_wf['DRESADDRES'] = non_wf['DRESADDRES'].str.replace(' {1,}', ' ')
non_wf['FID'] = non_wf.index

######## NO DIRECTION
nwf_1p = non_wf['DRESADDRES'].str.extract('^(\d*) +(%s) *(%s)' % (streetsort_str, abbrv_str)).dropna().join(non_wf[['FID', 'SZIP']]).rename(columns={0:'SNUM', 1:'STREET', 2:'STYPE'})

nwf_1p['STYPE'] = nwf_1p['STYPE'].str.replace(' ', '').map(pd.Series(abbrv.set_index(0)[1])).fillna(nwf_1p['STYPE']).str.replace(' ', '')
 
sixthpass = pd.merge(nwf_1p, df_dd, on=['SNUM', 'STREET', 'STYPE'], suffixes=['_MCDPH', '_ASSESS'])

######## MISSING/NONSTANDARD STREET TYPE 
nwf_2p = non_wf['DRESADDRES'].str.extract('^(\d*) *(W|N|E|S|WEST|NORTH|EAST|SOUTH) *(%s)$' % (streetsort_str)).dropna().join(non_wf[['FID', 'SZIP']]).rename(columns={0:'SNUM', 1:'DIR', 2:'STREET'})
 
seventhpass = pd.merge(nwf_2p, df_dd, on=['SNUM', 'DIR', 'STREET'], suffixes=['_MCDPH', '_ASSESS'])

######## MISSING STREET TYPE AND APT

comp_nwf = non_wf.drop(sixthpass['FID'].unique()).drop(seventhpass['FID'].unique())

nwf_3p = comp_nwf['DRESADDRES'].str.extract('^(\d*) *(W|N|E|S|WEST|NORTH|EAST|SOUTH) *(%s).*(APT|BLDG|#)' % (streetsort_str)).dropna().join(non_wf[['FID', 'SZIP']]).rename(columns={0: 'SNUM', 1:'DIR', 2:'STREET'})

eighthpass = pd.merge(nwf_3p, df_dd, on=['SNUM', 'DIR', 'STREET'], suffixes=['_MCDPH', '_ASSESS'])


comp_nwf_2 = comp_nwf.drop(eighthpass['FID'].unique())

####### MISSPELLINGS--PREP FUZZY MATCH
apts = pd.concat([comp_nwf_2, comp_nwf_2['DRESADDRES'].str.extract('(.*) +(#|APT|BLDG)').dropna()[0]], axis=1, join='inner')
apts['DRESADDRES'] = apts[0]
del apts[0]

nonapt = comp_nwf_2.drop(apts.index)

fuzzy_df = pd.concat([apts, nonapt], axis=0)

nwf_4p = fuzzy_df['DRESADDRES'].str.extract("(\d+) *(N\.?|S\.?|E\.?|W\.?) +([A-Z,0-9, ,-,',\.]*) *( %s)$" % (abbrv_str)).dropna()
nwf_4p.columns = ['SNUM', 'DIR', 'STREET', 'STYPE']

nwf_4p['STYPE'] = nwf_4p['STYPE'].str.replace(' ', '').map(pd.Series(abbrv.set_index(0)[1])).fillna(nwf_4p['STYPE']).str.replace(' ', '')

re_add = nwf_4p[nwf_4p.columns[0]].str.cat(others=[nwf_4p[i] for i in nwf_4p.columns[1:]], sep=' ')  

re_adzip = pd.concat([re_add, comp_nwf_2['SZIP']], axis=1, join='inner').rename(columns={'SNUM':'SITUSADD'})

fuzzy_matches = re_adzip.copy()
fuzzy_matches['MATCH_ADD'] = ''
fuzzy_matches['MATCH_APN'] = ''
fuzzy_matches['MATCH_RATIO'] = 0.0

#u_stnm = pd.Series(street_names.unique())

for i in re_adzip.index:
    srcadd = re_adzip.loc[i, 'SITUSADD']
    srczip = re_adzip.loc[i, 'SZIP']
    print srcadd, srczip
    if srczip in df_dd['SZIP'].unique():
        src_df = df_dd['SITUSADD'].loc[df_dd['SZIP'] == srczip]
    else:
        src_df = df_dd['SITUSADD']
    f_r = src_df.apply(lambda x: fuzz.ratio(srcadd, x)).max()
    f_i = src_df.apply(lambda x: fuzz.ratio(srcadd, x)).idxmax()
    fuzzy_matches.loc[i, 'MATCH_RATIO'] = f_r
    fuzzy_matches.loc[i, 'MATCH_ADD'] = src_df.loc[f_i]
    fuzzy_matches.loc[i, 'MATCH_APN'] = df_dd.loc[f_i, 'APN']
    print srcadd, f_r, f_i

print fuzzy_matches[fuzzy_matches['MATCH_RATIO'] > 80].sort('MATCH_RATIO', ascending=False)

