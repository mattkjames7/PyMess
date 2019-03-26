import numpy as np
from ._CFunctions import _CGammaSpouge

###### File created automatically using PopulateCtypes ######

def Gamma(z):

	#Convert input variables to appropriate numpy dtype:
	_z = np.float64(z)
	if isinstance(_z,np.ndarray):
		res = np.zeros(_z.size,dtype='float64')
		for i in range(0,_z.size):
			res[i] = _CGammaSpouge(_z[i])
	else:
		res = _CGammaSpouge(_z)
	return res
