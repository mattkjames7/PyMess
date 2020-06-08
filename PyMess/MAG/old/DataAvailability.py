import numpy as np
from .. import Globals
from ..Tools.ListFiles import ListFiles

def DataAvailability(Minute=False,Type='MSO'):
	'''
	List all of the dates for which we have data.
	
	Inputs
	======
	Minute : boolean
		If True - check the minute resolution data
	Type : string
		'MSO'|'Rotated'|'MPN' for normal data in MSO coords, rotated
		into poloidal, toroidal and parallel, or magnetopause normal
		coordinates, respected.
		
	Returns
	=======
	dates : integer array
	
	'''
	#get the path to search in
	if Type == 'MSO':
		if Minute == True:
			path = Globals.MessPath+'MAG/Binary/MSO/Minute/'
		else:
			path = Globals.MessPath+'MAG/Binary/MSO/Full/'
	elif Type == 'Rotated':
		if Minute:
			path = Globals.MessPath+'MAG/Binary/Rotated/Minute/'
		else:
			path = Globals.MessPath+'MAG/Binary/Rotated/Full/'	
	elif Type == 'MPN':
		if Minute:
			path = Globals.MessPath+'MAG/Binary/MPN/Minute/'
		else:
			path = Globals.MessPath+'MAG/Binary/MPN/Full/'

	#scan for files
	_,fnames = ListFiles(path,ReturnNames=True)
	
	#convert to dates
	n = fnames.size
	dates = np.zeros(n,dtype='int32')
	for i in range(0,n):
		dates[i] = np.int32(fnames[i][:8])

	dates.sort()
	return dates
