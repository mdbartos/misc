import os
import pandas as pd
import numpy as np
import re

df = pd.read_csv('mc_assessor.txt', sep='\t')
df_sub = df[['OADDRESS1', 'OADDRESS2', 'OCITY', 'OSTATE', 'APN', 'SITUSADD', 'SSUITE', 'SCITY', 'SZIP', 'SUBDIVISIO']]
#df_sub.to_csv('mc_sub', sep='\t')
df_sub = df_sub.dropna(subset=['SITUSADD'])
