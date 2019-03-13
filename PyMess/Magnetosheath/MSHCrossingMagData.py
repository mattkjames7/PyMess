from .GetMSHCrossings import GetMSHCrossings
from ..MAG.MagDataMPN import MagDataMPN
from ..MAG.ReadMagData import ReadMagData
import RecarrayTools as RT
import DateTimeTools as TT
import numpy as np

def MSHCrossingMagData(Crossing,MagType='MSM',Ab=None,Minute=False,Res=None,Rsm=1.42):
	'''
	Reads in magnetometer data during the time of a magnetosheath
	crossing.
	
	Inputs:
		Crossing: Integer index for the crossing to get the data for.
		MagType: String to determine magnetometer data type -
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
	
	#now to select the required data product
	if MagType == 'MPN':
		DataFunc = MagDataMPN
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


