import numpy as np
from .. import Globals
import DateTimeTools as TT
from .GetMPCrossings import GetMPCrossings
import PyFileIO as pf

def SaveMSTimes():
	'''
	Save a list of the times when MESSENGER is within the magnetopause.
	
	'''
	
	#the file name
	fname = Globals.ModuleData + 'MSTimes.dat'
	
	#the output dtype
	dtype = [('Date0','int32'),('ut0','float32'),('Date1','int32'),('ut1','float32')]
	
	#get the crossings list
	mp = GetMPCrossings()
	
	#we want crossings where:
	# ctype[i] == 'i' and ctype[i+1] == 'o'
	# and the time difference is less than an orbit
	use = np.where((mp.ctype[:-1] == 'i') & (mp.ctype[1:] == 'o'))[0] 
	out = np.recarray(use.size,dtype=dtype)
	
	out.Date0 = mp.Date1[use]
	out.ut0 = mp.ut1[use]
	
	out.Date1 = mp.Date0[use+1]
	out.ut1 = mp.ut0[use+1]
	
	
	dt = np.zeros(use.size,dtype='float32')
	for i in range(use.size):
		dt[i] = TT.TimeDifference(mp.Date1[use[i]],mp.ut1[use[i]],mp.Date0[use[i]+1],mp.ut0[use[i]+1])
		
	use = np.where(dt < 12.0)[0]
	out = out[use]
	
	#save the file
	pf.WriteASCIIData(fname,out)
	
