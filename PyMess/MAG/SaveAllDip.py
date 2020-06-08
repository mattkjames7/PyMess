import numpy as np
from ._SaveDip import _SaveDip
from .DataAvailability import DataAvailability

	
def SaveAllDip(Minute=False,StartI=0,EndI=None):
	'''
	This procedure should save all magnetometer data rotated into 
	a coordinate system useful for studying waves, with components in
	the poloidal, toroidal and parallel directions.
	
	Inputs:
		Minute: Set to True to use minute resolution data, or False for
			full time resolution data.
		res: Tells the function to resample the MAG data to this time
			resolution in seconds.
		ModelParams: Parameters to use for the KT17 magnetic field model
			When set to None, the values used are calculated based on 
			Mercury's distance from the Sun.
		Ab: Aberration angle in degrees, set to None to calculate 
			automatically.
		DetectGaps: If not None, then the routine will search for gaps
			larger than DetectGaps in hours and insert NaNs, gaps 
			smaller than this are interpolated over.

	'''	
	dates = DataAvailability(Minute,Type='MSO')
	nf = np.size(dates)
	if EndI is None:
		EndI = nf
	for i in range(StartI,EndI):
		print('Converting File {0} of {1} ({2})'.format(i+1,nf,dates[i]))
		_SaveDip(dates[i],Minute)
