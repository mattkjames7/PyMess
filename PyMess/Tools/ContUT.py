import numpy as np
import copy
import DateTimeTools as TT

def ContUT(Date,ut):
	'''
	Calculate the continuous ut array
	'''
	utc = copy.deepcopy(ut).astype('float64')
	
	ud = np.unique(Date)
	nd = ud.size
	
	#date difference between 19500101 and 20000101
	dd2000 = 18262
	dtp = dd2000*24.0
	pd = 20000101
	for i in range(0,nd):
		use = np.where(Date == ud[i])[0]
		dt = np.float64(dtp) + np.float64(TT.DateDifference(pd,ud[i]))*np.float64(24.0)
		utc[use] = np.float64(ut[use]) + np.float64(dt)
		dtp = np.array(dt)
		pd = ud[i]
		
	return utc		
	
	
