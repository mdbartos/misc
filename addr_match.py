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
            self.match_df = df_sub.dropna(subset=[self.match_fields['address'], self.match_fields['id']])
            self.matched = pd.DataFrame(columns=match_fields.values())
#            self.unmatched = pd.DataFrame(columns=match_fields.values())

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

            self.matched = pd.DataFrame(columns=self.match_fields.values())
            self.unmatched = pd.DataFrame(columns=[self.match_fields['t_id'], self.match_fields['address'], self.match_fields['zip']])

    def wf_split(self):

            self.matched['FLAGS'] = ''

	    target_wf = self.target_df[self.match_fields['address']].str.extract('(\d*) *(N|W|E|S|NORTH|WEST|EAST|SOUTH) *(%s) *(%s)' % (self.streetsort_str, self.abbrv_str)).dropna()

	    target_wf_addr = target_wf[0] + ' ' + target_wf[1] + ' ' + target_wf[2] + target_wf[3]

	    self.target_wf = pd.DataFrame(target_wf_addr, columns=[self.match_fields['address']])
	    self.target_wf[self.match_fields['t_id']] = self.target_wf.index
	    self.target_wf = pd.concat([self.target_wf, self.target_df[self.match_fields['zip']]], axis=1, join='inner')

	    self.target_nwf = self.target_df.loc[~self.target_df.index.isin(self.target_wf.index)]
            self.target_nwf = self.target_nwf.loc[~(self.target_nwf[self.match_fields['address']].str.split().apply(lambda x: len(x)) == 1)]    #GEN
	    self.target_nwf[self.match_fields['address']] = self.target_nwf[self.match_fields['address']].str.replace(' {1,}', ' ')
#	    self.target_nwf['FID'] = self.target_nwf.index

            self.unmatched = self.unmatched.append(self.target_wf).append(self.target_nwf)

    def wf_parse(self):
            
            #### FIRST PASS--EXTRANEOUS INFORMATION (APT, BLDG, etc.)

            firstpass = pd.merge(self.target_wf, self.match_wf, on=self.match_fields['address'], how='inner', suffixes=['_TARGET', '_MATCH']).drop_duplicates(subset=[self.match_fields['t_id']])

            firstpass['FLAGS'] = 'ndst'
            self.matched = pd.concat([self.matched, firstpass], axis=0)
            self.unmatched = self.unmatched.drop(firstpass[self.match_fields['t_id']].unique())

            comp_firstpass = self.target_wf.loc[~self.target_wf.index.isin(firstpass[self.match_fields['t_id']])]

            comp_firstpass['SNUM'] = comp_firstpass[self.match_fields['address']].str.extract('(\d*) *(N|W|E|S|NORTH|WEST|EAST|SOUTH) *(%s) *(%s)' % (self.streetsort_str, self.abbrv_str))[0]

            comp_firstpass['DIR'] = comp_firstpass[self.match_fields['address']].str.extract('(\d*) *(N|W|E|S|NORTH|WEST|EAST|SOUTH) *(%s) *(%s)' % (self.streetsort_str, self.abbrv_str))[1].str.replace('NORTH','N').str.replace('SOUTH','S').str.replace('WEST','W').str.replace('EAST','E') 

            comp_firstpass['STREET'] = comp_firstpass[self.match_fields['address']].str.extract('(\d*) *(N|W|E|S|NORTH|WEST|EAST|SOUTH) *(%s) *(%s)' % (self.streetsort_str, self.abbrv_str))[2]

            comp_firstpass['STYPE'] = comp_firstpass[self.match_fields['address']].str.extract('(\d*) *(N|W|E|S|NORTH|WEST|EAST|SOUTH) *(%s) *(%s)' % (self.streetsort_str, self.abbrv_str))[3].str.replace(' ', '')

            comp_firstpass['STYPE'] = comp_firstpass['STYPE'].map(pd.Series(self.abbrv.set_index(0)[1])).fillna(comp_firstpass['STYPE'])


            #### SECOND PASS--DIFFERENT CARDINAL DIRECTION

            secondpass = pd.merge(comp_firstpass, self.match_wf, on=['SNUM', 'DIR', 'STREET', 'STYPE'], how='inner', suffixes=['_TARGET', '_MATCH']).drop_duplicates(subset=[self.match_fields['t_id']])

            self.matched = pd.concat([self.matched, secondpass], axis=0)            
            self.unmatched = self.unmatched.drop(secondpass[self.match_fields['t_id']].unique())


            comp_secondpass = comp_firstpass[~comp_firstpass.index.isin(secondpass[self.match_fields['t_id']])]

            #### THIRD PASS--NON-MATCHING STREET NUMBER

            test = pd.merge(comp_secondpass[comp_secondpass['SNUM'] != ''], self.match_wf[self.match_wf['SNUM'] != ''], on=['DIR', 'STREET', 'STYPE', self.match_fields['zip']], suffixes=['_TARGET', '_MATCH']).set_index(self.match_fields['t_id']).reset_index()

            test['SNUM_DIFF'] = (test['SNUM_TARGET'].astype(int) - test['SNUM_MATCH'].astype(int))  

            test['SNUM_ABS'] = (test['SNUM_TARGET'].astype(int) - test['SNUM_MATCH'].astype(int)).apply(lambda x: abs(x))

            thirdpass = pd.DataFrame(columns=test.columns)

            for i in test[self.match_fields['t_id']].unique():
                t = test[test[self.match_fields['t_id']] == i]
                lo = t[t['SNUM_DIFF'] < 0]
                hi = t[t['SNUM_DIFF'] > 0]

                if len(lo) > 0:
                    ixmin_lo = lo['SNUM_ABS'].idxmin()
                    thirdpass = thirdpass.append(t.loc[ixmin_lo])

                if len(hi) > 0:
                    ixmin_hi = hi['SNUM_ABS'].idxmin()
                    thirdpass = thirdpass.append(t.loc[ixmin_hi])

            self.matched = pd.concat([self.matched, thirdpass.drop_duplicates(self.match_fields['t_id'])], axis=0) #### NEEDS TO BE FIXED
            self.unmatched = self.unmatched.drop(thirdpass[self.match_fields['t_id']].unique())

            comp_thirdpass = comp_secondpass[~comp_secondpass.index.isin(thirdpass[self.match_fields['t_id']].unique())]

            #### FOURTH PASS--NON-MATCHING DIRECTION

            fourthpass = pd.merge(comp_thirdpass[comp_thirdpass['SNUM'] != ''], self.match_wf[self.match_wf['SNUM'] != ''], on=['SNUM', 'STREET', 'STYPE', self.match_fields['zip']], suffixes=['_TARGET', '_MATCH'])

            comp_fourthpass = comp_thirdpass[~comp_thirdpass.index.isin(fourthpass[self.match_fields['t_id']].unique())]

            self.matched = pd.concat([self.matched, fourthpass], axis=0)
            self.unmatched = self.unmatched.drop(fourthpass[self.match_fields['t_id']].unique())


            #### FIFTH PASS--NON-MATCHING STREET TYPE

            fifthpass = pd.merge(comp_fourthpass[comp_fourthpass['SNUM'] != ''], self.match_wf[self.match_wf['SNUM'] != ''], on=['SNUM', 'STREET', 'DIR', self.match_fields['zip']], suffixes=['_TARGET', '_MATCH'])

            self.matched = pd.concat([self.matched, fifthpass], axis=0)
            self.unmatched = self.unmatched.drop(fifthpass[self.match_fields['t_id']].unique())

            
            self.firstpass = firstpass
            self.secondpass = secondpass
            self.thirdpass = thirdpass
            self.fourthpass = fourthpass
            self.fifthpass = fifthpass
            
    def nwf_parse(self):
        
        nwf_1p = self.target_nwf[self.match_fields['address']].str.extract('^(\d*) +(%s) *(%s)' % (self.streetsort_str, self.abbrv_str)).dropna().join(self.target_nwf[[self.match_fields['t_id'], self.match_fields['zip']]]).rename(columns={0:'SNUM', 1:'STREET', 2:'STYPE'})

        nwf_1p['STYPE'] = nwf_1p['STYPE'].str.replace(' ', '').map(pd.Series(self.abbrv.set_index(0)[1])).fillna(nwf_1p['STYPE']).str.replace(' ', '')
        
        sixthpass = pd.merge(nwf_1p, self.match_wf, on=['SNUM', 'STREET', 'STYPE'], suffixes=['_TARGET', '_MATCH'])
        self.matched = pd.concat([self.matched, sixthpass], axis=0)
        self.unmatched = self.unmatched.drop(sixthpass[self.match_fields['t_id']].unique())


        ######## MISSING/NONSTANDARD STREET TYPE 
        nwf_2p = self.target_nwf[self.match_fields['address']].str.extract('^(\d*) *(W|N|E|S|WEST|NORTH|EAST|SOUTH) *(%s)$' % (self.streetsort_str)).dropna().join(self.target_nwf[[self.match_fields['t_id'], self.match_fields['zip']]]).rename(columns={0:'SNUM', 1:'DIR', 2:'STREET'})
        
        seventhpass = pd.merge(nwf_2p, self.match_wf, on=['SNUM', 'DIR', 'STREET'], suffixes=['_TARGET', '_MATCH'])
        self.matched = pd.concat([self.matched, seventhpass], axis=0)
        self.unmatched = self.unmatched.drop(seventhpass[self.match_fields['t_id']].unique())

        ######## MISSING STREET TYPE AND APT

        comp_nwf = self.target_nwf.drop(sixthpass[self.match_fields['t_id']].unique()).drop(seventhpass[self.match_fields['t_id']].unique())

        nwf_3p = comp_nwf[self.match_fields['address']].str.extract('^(\d*) *(W|N|E|S|WEST|NORTH|EAST|SOUTH) *(%s).*(APT|BLDG|#)' % (self.streetsort_str)).dropna().join(self.target_nwf[[self.match_fields['t_id'], self.match_fields['zip']]]).rename(columns={0: 'SNUM', 1:'DIR', 2:'STREET'})

        eighthpass = pd.merge(nwf_3p, self.match_wf, on=['SNUM', 'DIR', 'STREET'], suffixes=['_TARGET', '_MATCH'])
        self.matched = pd.concat([self.matched, eighthpass], axis=0)
        self.unmatched = self.unmatched.drop(eighthpass[self.match_fields['t_id']].unique())


        comp_nwf_2 = comp_nwf.drop(eighthpass[self.match_fields['t_id']].unique())

        ####### MISSPELLINGS--PREP FUZZY MATCH
        apts = pd.concat([comp_nwf_2, comp_nwf_2[self.match_fields['address']].str.extract('(.*) +(#|APT|BLDG)').dropna()[0]], axis=1, join='inner')
        apts[self.match_fields['address']] = apts[0]
        del apts[0]

        nonapt = comp_nwf_2.drop(apts.index)

        fuzzy_df = pd.concat([apts, nonapt], axis=0)

        nwf_4p = fuzzy_df[self.match_fields['address']].str.extract("(\d+) *(N\.?|S\.?|E\.?|W\.?) +([A-Z,0-9, ,-,',\.]*) *( %s)$" % (self.abbrv_str)).dropna()
        nwf_4p.columns = ['SNUM', 'DIR', 'STREET', 'STYPE']

        nwf_4p['STYPE'] = nwf_4p['STYPE'].str.replace(' ', '').map(pd.Series(self.abbrv.set_index(0)[1])).fillna(nwf_4p['STYPE']).str.replace(' ', '')

        re_add = nwf_4p[nwf_4p.columns[0]].str.cat(others=[nwf_4p[i] for i in nwf_4p.columns[1:]], sep=' ')  

        re_adzip = pd.concat([re_add, comp_nwf_2[self.match_fields['zip']]], axis=1, join='inner').rename(columns={'SNUM':self.match_fields['address']})

        re_adzip[self.match_fields['t_id']] = re_adzip.index

        fuzzy_matches = re_adzip.copy()
        fuzzy_matches['MATCH_ADD'] = ''
        fuzzy_matches['MATCH_APN'] = ''
        fuzzy_matches['MATCH_RATIO'] = 0.0

        #u_stnm = pd.Series(street_names.unique())

        for i in re_adzip.index:
            srcadd = re_adzip.loc[i, self.match_fields['address']]
            srczip = re_adzip.loc[i, self.match_fields['zip']]
            print srcadd, srczip
            if srczip in self.match_wf[self.match_fields['zip']].unique():
                src_df = self.match_wf[self.match_fields['address']].loc[self.match_wf[self.match_fields['zip']] == srczip]
            else:
                src_df = self.match_wf[self.match_fields['address']]
            f_r = src_df.apply(lambda x: fuzz.ratio(srcadd, x)).max()
            f_i = src_df.apply(lambda x: fuzz.ratio(srcadd, x)).idxmax()
            fuzzy_matches.loc[i, 'MATCH_RATIO'] = f_r
            fuzzy_matches.loc[i, 'MATCH_ADD'] = src_df.loc[f_i]
            fuzzy_matches.loc[i, 'MATCH_APN'] = self.match_wf.loc[f_i, 'APN']
            print srcadd, f_r, f_i
            

        self.sixthpass = sixthpass
        self.seventhpass = seventhpass
        self.eighthpass = eighthpass
        self.ninthpass = fuzzy_matches

        self.matched = pd.concat([self.matched, fuzzy_matches], axis=0)
        self.unmatched = self.unmatched.drop(fuzzy_matches[self.match_fields['t_id']].unique())


#### CALL METHOD

b = addr_match('/home/akagi/Desktop/assessor/mc_assessor.txt', sep='\t')
b.abbrv_init('/home/akagi/Desktop/assessor/usps_abbrv.csv', header=None)
b.prep_match()
b.target_init('/home/akagi/Desktop/MCDPH_data/csv/DeathAddress.csv')
b.wf_split()
b.wf_parse()
b.nwf_parse()
