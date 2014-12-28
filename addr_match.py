import os
import pandas as pd
import numpy as np
from fuzzywuzzy import fuzz
from fuzzywuzzy import process

#match flags: z: zip, n: street number, d: direction, s: street name, t: street type

class addr_match():
	def __init__(self, match_path, match_fields={'address':'SITUSADD', 'zip': 'SZIP', 'id': 'APN'}, **kwargs):
		
		self.match_fields = match_fields
		df = pd.read_csv(match_path, **kwargs)
		df_sub = df[match_fields.values()]
		self.match_df = df_sub.dropna()

	def abbrv_init(self, abbrv_path, **kwargs):
		abbrv = pd.read_csv(abbrv_path, **kwargs)
		abbrv[1] = abbrv[1].str.replace('[^A-Z]', '')
		abbrv[0] = abbrv[0].str.replace(' ', '')
		abbrv.loc[abbrv[0] == 'WAY', 1] = 'WY'
		abbrv_li = list(abbrv[1])
		additions = ['HAVEN', 'GLEN', 'GLENN', 'WAY', 'TR', 'PT', 'POINT', 'HW', 'LP', 'PW', 'PZ', 'COURT', 'GAP', 'HOLLOW', 'STR', 'CROSSING', 'PLACE', 'PKY', 'ALLEY', 'AVENUE', 'BOULEVARD', 'DRIVE', 'ROAD', 'FREEWAY', 'HIGHWAY', 'LANE', 'PARKWAY', 'WALK', 'CENTER', 'CIRCLE', 'STREET'] 
		abbrv_li.extend(additions)
		abbrv_str = '| '.join(abbrv_li)
		self.abbrv = abbrv
		self.abbrv_str = abbrv_str

	def prep_match(self):

		type1 = self.match_df[self.match_fields['address']].str.extract("(\d*) *(N\.?|S\.?|E\.?|W\.?) +([A-Z,0-9, ,-,',\.]*) *( %s)$" % (self.abbrv_str))

		nontype1 = self.match_df.loc[~self.match_df[self.match_fields['address']].str.contains("(\d*) *(N\.?|S\.?|E\.?|W\.?) +([A-Z,0-9, ,-,',\.]*) *( %s)$" % (self.abbrv_str))]

		type2 = nontype1[self.match_fields['address']].loc[nontype1[self.match_fields['address']].str.contains(" [N\.?|W\.?|S\.?|E\.?] ")].str.extract("(\d*) *(N\.?|S\.?|E\.?|W\.?) +([A-Z,0-9, ,-,',\.]*)$")

		type3 = nontype1[self.match_fields['address']].loc[~nontype1[self.match_fields['address']].str.contains(" [N\.?|W\.?|S\.?|E\.?] ")].str.extract("(\d*) *([A-Z,0-9, ,-,',\.]*)( %s)$" % (self.abbrv_str))

		type1_names = pd.DataFrame(type1.dropna()[[0,1,2,3]]).rename(columns={0:'SNUM', 1:'DIR', 2:'STREET', 3:'STYPE'})
		type2_names = pd.DataFrame(type2.dropna()[[0,2]]).rename(columns={0:'SNUM',1:'DIR', 2:'STREET'})
		
		type3_names = pd.DataFrame(type3.dropna()[[0,1]]).rename(columns={0:'SNUM', 1:'STREET', 2:'STYPE'})
		

#### CREATE STREET NAME SERIES
		street_loc = pd.concat([type1_names, type2_names, type3_names], axis=0)
		street_names = street_loc['STREET']
		street_names = street_names.drop(street_names[street_names.str.len() == 1].index)
		self.street_names = street_names.drop(street_names[street_names.isin(['RD', 'PL', 'LP', 'DR', 'HWY', 'OLD', 'VIS'])].index)

#### CREATE SORTED STREET NAME STRING

		streetsort = pd.DataFrame(street_names.unique())
		streetsort['len'] = streetsort[0].str.len()
		self.streetsort_str = '|'.join(streetsort.sort('len', ascending=False)[0].values)

		self.match_df = pd.concat([self.match_df, street_loc], axis=1)
		self.match_df['STYPE'] = self.match_df['STYPE'].str.replace(' ', '')

		self.match_wf = self.match_df.drop_duplicates(subset=[self.match_fields['address']])[[self.match_fields['address'], self.match_fields['id'], 'SNUM', 'DIR', 'STREET', 'STYPE', self.match_fields['zip']]]

		self.match_wf[self.match_fields['address']] = self.match_wf[self.match_fields['address']].str.replace('.', '').str.replace(',', '')

		self.match_wf['STYPE'] = self.match_wf['STYPE'].map(pd.Series(self.abbrv.set_index(0)[1])).fillna(self.match_wf['STYPE'])


	def target_init(self, target_path, match_fields={'address':'DRESADDRES', 'zip':'DRESZIP', 'id':'FID_1'}, **kwargs):
		self.match_fields['t_id'] = match_fields['id']
		self.target_df = pd.read_csv(target_path, **kwargs).rename(columns={match_fields['address'] : self.match_fields['address'], match_fields['zip'] : self.match_fields['zip']}).dropna(subset=[self.match_fields['address']]).set_index(self.match_fields['t_id'], drop=False)

		self.target_df[self.match_fields['address']] = self.target_df[self.match_fields['address']].str.upper().str.replace('.', '').str.replace(',', '')

	def wf_split(self):

		target_wf = self.target_df[self.match_fields['address']].str.extract('(\d*) *(N|W|E|S|NORTH|WEST|EAST|SOUTH) *(%s) *(%s)' % (self.streetsort_str, self.abbrv_str)).dropna()

		target_wf_addr = target_wf[0] + ' ' + target_wf[1] + ' ' + target_wf[2] + target_wf[3]

		self.target_wf = pd.DataFrame(target_wf_addr, columns=[self.match_fields['address']])
		self.target_wf[self.match_fields['t_id']] = self.target_wf.index
		self.target_wf = pd.concat([self.target_wf, self.target_df[self.match_fields['zip']]], axis=1, join='inner')

		self.target_nwf = self.target_df.loc[~self.target_df.index.isin(self.target_wf.index)]
#		target_nwf = target_nwf.loc[~(target_nwf['DRESADDRES'] == 'UNKNOWN')]
		self.target_nwf[self.match_fields['address']] = self.target_nwf[self.match_fields['address']].str.replace(' {1,}', ' ')
#		self.target_nwf['FID'] = self.target_nwf.index

	def parse_wf(self):
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



#### CALL METHOD

b = addr_match('/home/akagi/Desktop/assessor/mc_assessor.txt', sep='\t')
b.abbrv_init('/home/akagi/Desktop/assessor/usps_abbrv.csv', header=None)
b.prep_match()
b.target_init('/home/akagi/Desktop/MCDPH_data/csv/DeathAddress.csv')
b.wf_split()
