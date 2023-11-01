import numpy as np
from ..MAG.GetData import GetData
from .BdotBmp import BdotBmp
import RecarrayTools as RT
import DateTimeTools as TT
from .GetMPCrossings import GetMPCrossings

def MPCrossingMagData(Crossing,Type='MPN',Ab=None,Minute=False,Res=None,
		Rsm=1.42,Padding=0.0,DetectGaps=None,Autosave=True,Verbose=True,
		MagType='B.Bmp'):
	'''
	Reads in magnetometer data around the time of a MP crossing.
	
	Inputs:
		Crossing: Integer index for the crossing to get the data for.
		MagType: String to determine magnetometer data type -
			'MSM'|'MPN'|'Dip'|'B.Bmp'
		Ab: Aberration angle of the magnetosphere in degrees; when set 
			to None, this angle is automatically calculated.
		Minute: Boolean, when True, will load minute resolution data.
		Res: Resampling interval in seconds, if set to Non, then no
			resampling is performed.
		Rsm: Distance to subsolar point of the magnetopause in Rm.
		Padding: Time to add both before and after the MP crossing in
			hours.
			
	Returns:
		numpy.recarray
	'''
	#read in MP data and select the desired crossing
	mpc = GetMPCrossings()
	mpc = mpc[Crossing]
	
	#add the required padding in time
	ut0 = mpc.ut0 - Padding
	if ut0 < 0.0:
		ut0 += 24.0
		date0 = TT.MinusDay(mpc.Date0)
	else:
		date0 = mpc.Date0
	ut1 = mpc.ut1 + Padding
	if ut1 >= 24.0:
		ut1 -= 24.0
		date1 = TT.PlusDay(mpc.Date1)
	else:
		date1 = mpc.Date1	
	
	#now to select the required data product
	if MagType == 'B.Bmp':
		data = GetData([date0,date1],ut=[ut0,ut1],Minute=Minute,res=Res,Type='MSM',
				DetectGaps=DetectGaps,Autosave=Autosave,Ab=Ab,Verbose=Verbose)
		data = BdotBmp([date0,date1],ut=[ut0,ut1],Minute=Minute,res=Res,indata=data)
	else:
		data = GetData([date0,date1],ut=[ut0,ut1],Minute=Minute,res=Res,Type=Type,
				DetectGaps=DetectGaps,Autosave=Autosave,Ab=Ab,Verbose=Verbose)

		
	return data
