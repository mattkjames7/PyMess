from ._Dip import _Dip
import RecarrayTools as RT
import os
from . import MagGlobals

def _SaveDip(Date,Minute=False):
	'''
	This procedure should save magnetometer data rotated into 
	a coordinate system useful for studying waves, with components in
	the poloidal, toroidal and parallel directions.
	
	Inputs:
		Date: 32-bit integer containing the date with the format 
			yyyymmdd.
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
	path = MagGlobals.paths['Dip']
	if Minute:
		path += 'Minute/'
	else:
		path += 'Full/'

	if not os.path.isdir(path):
		os.system('mkdir -pv '+path)
	fname = path + '{:08d}.bin'.format(Date)
	data = _Dip(Date,Minute)
	if data.size > 0:
		RT.SaveRecarray(data,fname)
		return True
	else:
		return False
