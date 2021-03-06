import pandas as pd
import numpy as np

def trnsys_parser(filename, outfilename, **kwargs):

    f = open(filename, 'r')
    r = f.readlines()[0].replace(' ', '').replace(',', '').replace('\r', '').replace('\n', '')
    f.close()
    col_names = [i for i in r.split('\t') if i != '']
    ncols = len(col_names)
    print col_names
    print ncols
    
    infile = pd.read_csv(filename, skiprows=2, header=None, **kwargs)

    outfile = pd.DataFrame(index=range(len(infile)/ncols))

    for n in range(ncols):
        sub_idx = range(n, len(infile), ncols)
        sub_df = np.asarray(infile.iloc[sub_idx])

        outfile[col_names[n]] = sub_df

    outfile.to_csv(outfilename)
    
    return outfile



#### FUNCTION PARAMETERS:
# filename = input file name
# outfile name = name of output file
# ncols = number of columns
# **kwargs = optional keyword arguments: in this case, column names.

#### EXAMPLE USAGE:

#trnsys_parser('file.csv', 'newfile.csv', 5)

#### COLUMN NAMES CAN BE SUPPLIED OPTIONALLY:

#trnsys_parser('file.csv', 'newfile.csv', 5, col_names=['time', 'node1', 'node2', 'node3', 'outside_temp'])

