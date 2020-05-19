import numpy as np
from ... import Globals
from .ReadData import ReadData
import os
import RecarrayTools as RT

def _DateStrToDateUT(s):
	'''
	convert date on the format YYYY-MM-DDThh:mm:ss.sss to an integer date
	and a floating point time.
	'''
	Y = np.array([np.int32(x[0:4]) for x in s])
	M = np.array([np.int32(x[5:7]) for x in s])
	D = np.array([np.int32(x[8:10]) for x in s])
	h = np.array([np.float32(x[11:13]) for x in s])
	m = np.array([np.float32(x[14:16]) for x in s])
	s = np.array([np.float32(x[17:]) for x in s])

	Date = (Y*10000 + M*100 + D).astype('int32')
	ut = (h + m/60.0 + s/3600.0).astype('float32')
	
	return Date,ut
	

def ConvertData():
	'''
	Convert the James et al 2020 data to binaries
	
	'''
	#create the output dtype
	dtype = [	('Date','int32'),
				('ut','float32'),
				('nk','float32'),
				('tk','float32'),
				('K','float32'),
				('SplitProb','float32',(8,)),
				('Prob','float32'),
				('SplitClass','int8',(8,)),
				('Class','int8')]
				
	#read in the data file
	data = ReadData()
	
	#create a recarray
	out = np.recarray(data.size,dtype=dtype)
	
	#convert dates and times
	out.Date,out.ut = _DateStrToDateUT(data.UT)

	#copy the other fields across
	out.nk = data.Density
	out.tk = data.Temperature
	out.K = data.Kappa
	for i in range(0,8):
		out.SplitProb[:,i] = data['P{:d}'.format(i)].astype('float32')
		out.SplitClass[:,i] = data['Class{:d}'.format(i)].astype('int8')
	out.Prob = data.P
	out.Class = data.Class

	#find the unique dates
	ud = np.unique(out.Date)
	
	#create the output directory
	outdir = Globals.MessPath + 'FIPS/ANN/bin/'
	if not os.path.isdir(outdir):
		os.system('mkdir -pv '+outdir)
	
	#file name format
	fnfmt = outdir + '{:08d}.bin'
	
	
	#loop through dates, saving a recarray file for each one
	for i in range(ud.size):
		use = np.where(out.Date == ud[i])[0]

		fname = fnfmt.format(ud[i])
		
		RT.SaveRecarray(out[use],fname)
