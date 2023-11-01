from .GetMSHCrossings import GetMSHCrossings
from ..MAG.GetData import GetData

import RecarrayTools as RT
import DateTimeTools as TT
import numpy as np

def MSHCrossingMagData(Crossing,Type='MSM',Ab=None,Minute=False,Res=None,Rsm=1.42,DetectGaps=None,Autosave=True,Verbose=True,MagType='MSM'):
	'''
	Reads in magnetometer data during the time of a magnetosheath
	crossing.
	
	Inputs:
		Crossing: Integer index for the crossing to get the data for.
		Type: String to determine magnetometer data type -
			'MSM'|'MPN'
		Ab: Aberration angle of the magnetosphere in degrees; when set 
			to None, this angle is automatically calculated.
		Minute: Boolean, when True, will load minute resolution data.
		Res: Resampling interval in seconds, if set to Non, then no
			resampling is performed.
		Rsm: Distance to subsolar point of the magnetopause in Rm.

			
	Returns:
		numpy.recarray
	'''	
	#read in MSH crossing list
	mshc = GetMSHCrossings()
	mshc = mshc[Crossing]
	date0 = mshc.Date0
	date1 = mshc.Date1
	ut0 = mshc.ut0
	ut1 = mshc.ut1
	
	data = GetData([date0,date1],ut=[ut0,ut1],Minute=Minute,res=Res,Type=Type,
				DetectGaps=DetectGaps,Autosave=Autosave,Ab=Ab,Verbose=Verbose)
		
	return data


