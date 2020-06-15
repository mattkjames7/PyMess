import numpy as np
from .. import Globals
from ..Tools.ListFiles import ListFiles
from .ReadData import fipsdict

def DataAvailability(Type='60H'):
	'''
	List all of the dates for which we have data.
	
	Inputs
	======

	Type : string
		'edr'|'cdr'|'espec'|'ntp'|'ann'|'60H'|'60He'|'60He2'|'60Na'|'60O'|'10H'
		
	Returns
	=======
	dates : integer array
	
	'''
	#get the path to search in
	path,_,_ = fipsdict[Type]
	path = Globals.MessPath + 'FIPS/' + path
	
	#scan for files
	_,fnames = ListFiles(path,ReturnNames=True)

	#convert to dates
	n = fnames.size
	dates = np.zeros(n,dtype='int32')
	
	for i in range(0,n):
		l = len(fnames[i])
		dates[i] = np.int32(fnames[i][l-12:l-4])

	dates.sort()
	return dates
