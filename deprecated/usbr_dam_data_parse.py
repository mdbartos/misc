import os
import numpy as np
import pandas as pd

#get accumulations
for fn in os.listdir('.'):
	f = open(fn, 'r')
	lines = f.readlines()
	lines = pd.Series(lines)
	acclist = []
	#Get Accumulations for Month/Year
	for i, line in enumerate(lines):
		if 'ACCUMULATIONS FOR' in line:
			for j in lines[i:]:
				if 'TOTAL' not in j:
					acclist.append(j)
					print j
				else:
					break
	tempfile = open("accum_%s" % (fn), 'w')
	for i in acclist:
		tempfile.write(i)
	f.close()

#get elevations
for fn in os.listdir('.'):
	f = open(fn, 'r')
	lines = f.readlines()
	lines = pd.Series(lines)
	elevlist = []
	#Get elevations for Month/Year
	for i, line in enumerate(lines):
		if 'AVAILABLE RESERVOIR ELEVATIONS' in line:
			for j in lines[i:]:
				if '* BOTTOM' not in j:
					elevlist.append(j)
					print j
				else:
					break
	tempfile = open("elev_%s" % (fn), 'w')
	for i in elevlist:
		tempfile.write(i)
	f.close()

#get storage prj
for fn in os.listdir('.'):
	f = open(fn, 'r')
	lines = f.readlines()
	lines = pd.Series(lines)
	storlist = []
	#Get storage prj for Month/Year
	for i, line in enumerate(lines):
		if 'COLORADO RIVER STORAGE PROJECT DATA' in line:
			for j in lines[i:]:
				if 'TOT' not in j:
					storlist.append(j)
					print j
				else:
					break
	tempfile = open("stor_%s" % (fn), 'w')
	for i in storlist:
		tempfile.write(i)
	f.close()

#get losses
for fn in os.listdir('.'):
	f = open(fn, 'r')
	lines = f.readlines()
	lines = pd.Series(lines)
	losslist = []
	#Get losses for Month/Year
	for i, line in enumerate(lines):
		if 'HOOVER DAM LOSSES' in line:
			for j in lines[i:]:
				if 'TOTAL' not in j:
					losslist.append(j)
					print j
				else:
					break
	tempfile = open("loss_%s" % (fn), 'w')
	for i in losslist:
		tempfile.write(i)
	f.close()
