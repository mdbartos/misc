import pandas as pd
import numpy as np

def transys_parser(filename, outfilename, ncols, **kwargs):

    infile = pd.read_csv(filename, skiprows=2)

    outfile = pd.DataFrame(index=range(len(infile)/ncols))

    for n in range(ncols):
        sub_idx = range(n, len(infile), ncols)
        sub_df = np.asarray(infile.iloc[sub_idx])

        if 'col_names' in kwargs:
            outfile[kwargs['col_names'][n]] = sub_df
        else:
            outfile[n] = sub_df

    outfile.to_csv(outfilename)
    
    return outfile



#### FUNCTION PARAMETERS:
# filename = input file name
# outfile name = name of output file
# ncols = number of columns
# **kwargs = optional keyword arguments: in this case, column names.

#### EXAMPLE USAGE:

#transys_parser('file.csv', 'newfile.csv', 5)

#### COLUMN NAMES CAN BE SUPPLIED OPTIONALLY:

#transys_parser('file.csv', 'newfile.csv', 5, col_names=['time', 'node1', 'node2', 'node3', 'outside_temp'])

