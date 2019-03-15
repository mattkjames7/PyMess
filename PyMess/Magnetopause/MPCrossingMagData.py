import numpy as np
from ..MAG.MagDataMPN import MagDataMPN
from ..MAG.ReadMagData import ReadMagData
from ..MAG.ReadRotatedData import ReadRotatedData
from .BdotBmp import BdotBmp
import RecarrayTools as RT
import DateTimeTools as TT
from .GetMPCrossings import GetMPCrossings

def MPCrossingMagData(Crossing,MagType='MPN',Ab=None,Minute=False,Res=None,Rsm=1.42,Padding=0.0):
	'''
	Reads in magnetometer data around the time of a MP crossing.
	
	Inputs:
		Crossing: Integer index for the crossing to get the data for.
		MagType: String to determine magnetometer data type -
			'MSM'|'MPN'|'Rotated'|'B.Bmp'
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
	ut0 = mpc.ut0 - padding
	if ut0 < 0.0:
		ut0 += 24.0
		date0 = TT.MinusDay(mpc.Date0)
	else:
		date0 = mpc.Date0
	ut1 = mpc.ut1 + padding
	if ut1 >= 24.0:
		ut1 -= 24.0
		date1 = TT.PlusDay(mpc.Date1)
	else:
		date1 = mpc.Date1	
	
	#now to select the required data product
	if MagType == 'MPN':
		DataFunc = MagDataMPN
	elif MagType == 'Rotated':
		DataFunc = ReadRotatedData
	elif MagType == 'B.Bmp':
		DataFunc = BdotBmp
	else:
		DataFunc = ReadMagData

	#list all of the dates to load
	if date0 == date1:
		dates = [date0]
	else:
		dates = []
		d = date0
		while d <= date1:
			dates.append(d)
			d = TT.PlusDay(d)
			
	#now to load all of those dates
	nd = np.size(dates)
	data = DataFunc(dates[0],Minute=Minute,res=res,Ab=Ab)
	if nd > 1:
		for i in range(1,nd):
			tmp = DataFunc(dates[i],Minute=Minute,res=res,Ab=Ab)
			data = RT.JoinRecarray(data,tmp)	
	
	#now to remove anything that is out of the desired time range
	if nd == 1:
		use = np.where((data.ut >= ut0) & (data.ut <= ut1))[0]
	else:
		use = np.where((((data.Date == dates[0]) & (data.ut >= ut0)) |
						((data.Date == dates[-1]) & (data.ut <= ut1)) |
						((data.Date > dates[0]) & (data.Date < dates[-1]))))[0]
		
	return data[use]
