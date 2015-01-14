import subprocess as sub
import os

idx = range(2005,2105,5)

urlbase = 'http://cida.usgs.gov/thredds/fileServer/ICLUS/files/housing_density/hd_iclus_'  

scen = ['a2', 'b1', 'b2', 'bc']

for a in scen:
	for i in idx:
		cmd = "wget --random-wait -P /home/tabris/Downloads/iclus_density/%s/ %s%s/bhd_%s_0101%s.tif" % (a, urlbase, a, a, i)
		sub.call(cmd, shell=True)

