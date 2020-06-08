import numpy as np
from .MagRotatedData import MagRotatedData
import RecarrayTools as RT
import os
from .. import Globals
from .DataAvailability import DataAvailability

def SaveRotatedData(Date,Minute=False,res=None,ModelParams=None,Ab=None,DetectGaps=None):
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
	if Minute:
		path = Globals.MessPath+'MAG/Binary/Rotated/Minute/'
	else:
		path = Globals.MessPath+'MAG/Binary/Rotated/Full/'
	if not os.path.isdir(path):
		os.system('mkdir -pv '+path)
	fname = path + '{:08d}.bin'.format(Date)
	data = MagRotatedData(Date,Minute,res,ModelParams,Ab,DetectGaps)
	RT.SaveRecarray(data,fname)
	
def SaveAllRotatedData(Minute=False,res=None,ModelParams=None,Ab=None,DetectGaps=None,StartI=0):
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
	
	for i in range(StartI,nf):
		print('Converting File {0} of {1} ({2})'.format(i+1,nf,dates[i]))
		SaveRotatedData(dates[i],Minute,res,ModelParams,Ab,DetectGaps)
