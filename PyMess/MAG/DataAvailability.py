import numpy as np
from .. import Globals
from ..Tools.ListFiles import ListFiles
from . import MagGlobals

def DataAvailability(Minute=False,Type='MSO'):
	'''
	List all of the dates for which we have data.
	
	Inputs
	======
	Minute : boolean
		If True - check the minute resolution data
	Type : string
		'MSO'|'Dip'|'MPN' for normal data in MSO coords, rotated
		into poloidal, toroidal and parallel, or magnetopause normal
		coordinates, respected.
		
	Returns
	=======
	dates : integer array
	
	'''
	#get the path to search in
	path = MagGlobals.paths[Type]
	if Minute:
		path += 'Minute/'
	else:
		path += 'Full/'
	
	#scan for files
	_,fnames = ListFiles(path,ReturnNames=True)
	
	#convert to dates
	n = fnames.size
	dates = np.zeros(n,dtype='int32')
	for i in range(0,n):
		dates[i] = np.int32(fnames[i][:8])

	dates.sort()
	return dates
