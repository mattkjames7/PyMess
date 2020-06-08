import numpy as np
from ._MPN import _MPN
import RecarrayTools as RT
import os
from . import MagGlobals

def _SaveMPN(Date,Minute=False):
	'''
	This procedure should save magnetometer data rotated into 
	a coordinate system useful for studying waves, with components in
	the poloidal, toroidal and parallel directions.
	
	Inputs:
		Date: 32-bit integer containing the date with the format 
			yyyymmdd.
		Minute: Set to True to use minute resolution data, or False for
			full time resolution data.


	'''	
	path = MagGlobals.paths['MPN']
	if Minute:
		path += 'Minute/'
	else:
		path += 'Full/'

	if not os.path.isdir(path):
		os.system('mkdir -pv '+path)
	fname = path + '{:08d}.bin'.format(Date)
	data = _MPN(Date,Minute)
	if data.size > 0:
		RT.SaveRecarray(data,fname)
		return True
	else:
		return False
