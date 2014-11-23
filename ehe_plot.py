import os
import numpy as np
import pandas as pd

basepath = '/home/akagi/Dropbox/Southwest Heat Vulnerability Team Share/EHE_days'

county_li = ['la', 'phx']
model_li = ['csiro-mk3', 'gfdl-esm2g', 'mpi-esm-lr']
scen_li = ['26', '45', '85']

scen_d = {}

def agg_plots(county):
   
    df = pd.read_csv('%s/%s/historical/EHE-%s_hist.csv' % (basepath, county, county))

    df['date'] = pd.to_datetime(df['date'])
    df['year'] = [i.year for i in df['date']]
    
    df = df.groupby('year').size()
    scen_d['hist'] = df

    for m in model_li:
        for s in scen_li:
            df_10_30 = pd.read_csv('%s/%s/projection_2010-2030/EHE-%s_%s-%s_2010-2030.csv' % (basepath, county, county, m, s))
            df_30_50 = pd.read_csv('%s/%s/projection_2030-2050/EHE-%s_%s-%s_2030-2050.csv' % (basepath, county, county, m, s))
            df_50_70 = pd.read_csv('%s/%s/projection_2050-2070/EHE-%s_%s-%s_2050-2070.csv' % (basepath, county, county, m, s))
            df_70_90 = pd.read_csv('%s/%s/projection_2070-2090/EHE-%s_%s-%s_2070-2090.csv' % (basepath, county, county, m, s))
            df = pd.concat([df_10_30, df_30_50, df_50_70, df_70_90], axis=0)
            
            df['date'] = pd.to_datetime(df['date'])
            df['year'] = [i.year for i in df['date']]

            df = df.groupby('year').size()

            scen_d['%s_%s' % (m, s)] = df

#################################################

agg_plots('la')
export_df = pd.DataFrame.from_dict(scen_d)
export_df.to_csv('la_groupby_year.csv')

agg_plots('phx')
export_df = pd.DataFrame.from_dict(scen_d)
export_df.to_csv('phx_groupby_year.csv')

