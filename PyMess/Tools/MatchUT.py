import numpy as np


def MatchUT(ut0,ut1,dtmax=30.0/3600.0):
	'''
	Matches the times in ut0 and ut1 where possible.
	
	Inputs
	======
	ut0	: float array
		Array of times to match
	ut1 : float array
		Array of times to match
	dtmax : float
		Maximum time difference between ut0 and ut1 to constitute a match
		
	Returns
	=======
	idx : int32 array
		Array of indices of ut1 which match each value of ut0, a value 
		of -1 in idx[i] means that there is no matching ut1 for ut0[i],
		otherwise:
		
		ut1[idx[i]] ~ ut0[i]
	
	
	'''
	#create output array
	n = np.size(ut0)
	idx = np.zeros(n,dtype='int32') - 1
	dtmin = np.zeros(n,dtype='float32')
	
	#loop through each value
	for i in range(0,n):
		dt = np.abs(ut1 - ut0[i])
		I = dt.argmin()
		if dt[I] <= dtmax:
			idx[i] = I
		dtmin[i] = dt[I]
		
	#check that there aren't multiple values
	u,c = np.unique(idx[idx > -1],return_counts=True)
	
	mult = np.where(c > 1)[0]
	for i in range(0,mult.size):
		use = np.where(idx == u[mult[i]])[0]
		dtu = dtmin[use]
		bad = np.where(dtu > dtu.min())[0]
		idx[use[bad]] = -1
		
	return idx,dtmin
