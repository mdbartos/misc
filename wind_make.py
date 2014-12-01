import numpy as np
import pandas as pd
import os
import datetime

#windpath = '/home/tabris/Dropbox/Southwest Heat Vulnerability Team Share/ppdb_data/USGS_wind.csv'

#nrel_path = '/home/tabris/Downloads/nrel_wind'

class make_wind():
    def __init__(self, windpath='/home/tabris/Dropbox/Southwest Heat Vulnerability Team Share/ppdb_data/USGS_wind.csv', nrel_path = '/home/tabris/Downloads/nrel_wind'):
        self.windpath = windpath
        self.nrel_path = nrel_path
        self.df = pd.read_csv(self.windpath)
        self.gmw = self.df.groupby(['nrel_idx', 'mpower_coeff', 'rated_wspd', 'tower_h', 'rotor_s_a']).sum()['MW_turbine']
        self.gll = self.df.groupby(['nrel_idx', 'mpower_coeff', 'rated_wspd', 'tower_h', 'rotor_s_a']).last()[['lat_grid', 'lon_grid']]

        self.g = pd.concat([self.gmw, self.gll], axis=1) 

        self.hist_timeslicer = pd.date_range(start=datetime.datetime(1949,1,1), end=datetime.datetime(2009,12,31), freq='10min')

        self.fut_timeslicer = pd.date_range(start=datetime.datetime(2040,1,1), end=datetime.datetime(2060,1,1), freq='10min')

        self.hist_df = pd.DataFrame(index=self.hist_timeslicer)
        self.hist_df['year'] = [i.year for i in self.hist_df.index]
        self.hist_df['month'] = [i.month for i in self.hist_df.index]
        self.hist_df['day'] = [i.day for i in self.hist_df.index]
        self.hist_df['hour'] = [i.hour for i in self.hist_df.index]
        self.hist_df['minute'] = [i.minute for i in self.hist_df.index]

        self.fut_df = pd.DataFrame(index=self.fut_timeslicer)
        self.fut_df['year'] = [i.year for i in self.fut_df.index]
        self.fut_df['month'] = [i.month for i in self.fut_df.index]
        self.fut_df['day'] = [i.day for i in self.fut_df.index]
        self.fut_df['hour'] = [i.hour for i in self.fut_df.index]
        self.fut_df['minute'] = [i.minute for i in self.fut_df.index]

    def make_wind_outfiles(self, forcingpath='/home/chesterlab/Bartos/VIC/output/wind', outpath='/home/tabris/Desktop/wind_out'):
        for i in self.g.index:
            nrel_idx = i[0]
            mpower_coeff = i[1]
            rated_wspd = i[2]
            tower_h = i[3]
            rotor_s_a = i[4]
            lat_grid = self.g.loc[i, 'lat_grid']
            lon_grid = self.g.loc[i, 'lon_grid']
    
            turb_cap = 0.5*(i[1])*(i[2]**3)*(i[4])*1.2041/1000000
            mw = self.g.loc[i, 'MW_turbine']
            multiplier = mw/turb_cap
            print multiplier

########## NREL CURVE ##########################

            nrel_2004 = pd.read_csv('%s/%s/%s.csv' % (self.nrel_path, 2004, nrel_idx), skiprows=1, names=['date', 'wind', 'mw', 'score', 'correct'])[['date', 'wind']]
            nrel_2005 = pd.read_csv('%s/%s/%s.csv' % (self.nrel_path, 2005, nrel_idx), skiprows=1, names=['date', 'wind', 'mw', 'score', 'correct'])[['date', 'wind']]
            nrel_2006 = pd.read_csv('%s/%s/%s.csv' % (self.nrel_path, 2006, nrel_idx), skiprows=1, names=['date', 'wind', 'mw', 'score', 'correct'])[['date', 'wind']]

            nrel = pd.concat([nrel_2004, nrel_2005, nrel_2006])
            nrel['date'] = pd.to_datetime(nrel['date'])
#           nrel['year'] = [i.year for i in nrel['date']]
            nrel['month'] = [i.month for i in nrel['date']]
            nrel['day'] = [i.day for i in nrel['date']]
            nrel['hour'] = [i.hour for i in nrel['date']]
            nrel['minute'] = [i.minute for i in nrel['date']]

            h = nrel.groupby(['month', 'day', 'hour', 'minute']).mean()['wind'].reset_index()
            hmax = nrel.groupby(['month', 'day', 'hour', 'minute']).max()['wind'].reset_index().rename(columns={'wind':'windmax'})
            hmin = nrel.groupby(['month', 'day', 'hour', 'minute']).min()['wind'].reset_index().rename(columns={'wind':'windmin'})

######### GET FORCINGS #########################
            scen_forcings = {}
            for j in ['hist', 'echam_a1b', 'echam_a2', 'echam_b1', 'ukmo_a1b', 'ukmo_a2', 'ukmo_b1']:
                forcings = pd.read_csv('%s/%s/full_data_%s_%s' % (forcingpath, j, lat_grid, lon_grid), skiprows=6, sep='\t', names=['year', 'month', 'day', 'out_wind', 'out_density', 'out_pressure', 'out_vp', 'out_air_temp'])[['year', 'month', 'day', 'out_density', 'out_air_temp']]
                scen_forcings.update({j : forcings})

######### MAKE OUTFILES ########################
            
            for k in scen_forcings.keys():
                if k == 'hist':
                    m = pd.merge(self.hist_df, scen_forcings[k], on=['year', 'month', 'day'])[['year', 'month', 'day', 'hour', 'minute', 'out_density', 'out_air_temp']]
                else:
                    m = pd.merge(self.fut_df, scen_forcings[k], on=['year', 'month', 'day'])[['year', 'month', 'day', 'hour', 'minute', 'out_density', 'out_air_temp']]

                m = pd.merge(m, h, on=['month', 'day', 'hour', 'minute'])
                m = pd.merge(m, hmin, on=['month', 'day', 'hour', 'minute'])
                m = pd.merge(m, hmax, on=['month', 'day', 'hour', 'minute'])
                m = m.sort(['year', 'month', 'day', 'hour', 'minute'])
### med power
                m['wind_th'] = m['wind']*(tower_h/100.0)**0.143
                m['cap_mw'] = multiplier*0.5*(mpower_coeff)*(m['wind_th']**3)*(rotor_s_a)*(m['out_density'])/1000000
                m['cap_mw'].loc[m['wind_th'] >= rated_wspd] = multiplier*mw
                m['cap_mw'].loc[m['wind_th'] <= 3.0] = 0.0
                m['cap_mw'].loc[m['wind_th'] >= 25.0] = 0.0
                m['cap_mw'].loc[m['cap_mw'] >= multiplier*mw] = multiplier*mw

### hi power

                m['windmax_th'] = m['windmax']*(tower_h/100.0)**0.143
                m['capmax_mw'] = multiplier*0.5*(mpower_coeff)*(m['windmax_th']**3)*(rotor_s_a)*(m['out_density'])/1000000
                m['capmax_mw'].loc[m['windmax_th'] >= rated_wspd] = multiplier*mw
                m['capmax_mw'].loc[m['windmax_th'] <= 3.0] = 0.0
                m['capmax_mw'].loc[m['windmax_th'] >= 25.0] = 0.0
                m['capmax_mw'].loc[m['capmax_mw'] >= multiplier*mw] = multiplier*mw

### lo power

                m['windmin_th'] = m['windmin']*(tower_h/100.0)**0.143
                m['capmin_mw'] = multiplier*0.5*(mpower_coeff)*(m['windmin_th']**3)*(rotor_s_a)*(m['out_density'])/1000000
                m['capmin_mw'].loc[m['windmin_th'] >= rated_wspd] = multiplier*mw
                m['capmin_mw'].loc[m['windmin_th'] <= 3.0] = 0.0
                m['capmin_mw'].loc[m['windmin_th'] >= 25.0] = 0.0
                m['capmin_mw'].loc[m['capmin_mw'] >= multiplier*mw] = multiplier*mw
               
                m = m.groupby(['year', 'month', 'day', 'hour']).mean().reset_index()

                if not os.path.exists('%s/%s' % (outpath, k)):
                    os.mkdir('%s/%s' % (outpath, k))

                m.to_csv('%s/%s/%s_%s' % (outpath, k, k, nrel_idx), sep='\t')
