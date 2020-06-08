import numpy as np
from scipy.interpolate import InterpolatedUnivariateSpline
from ..Tools.RotTrans import RotTrans
import os
from ..Pos.GetAberrationAngle import GetAberrationAngle
from .. import Globals
import RecarrayTools as RT

def ReadMagData(Date,Minute=False,res=None,Ab=None,DetectGaps=None):
	'''
	Reads binary magnetometer data from MESSENGER.
	
	Args:
		Date:		32-bit(minimum) integer with date in format yyyymmdd.
		Minute:		If True - routing will read minute averages of MAG data,
					if False, then full resolution data will be read.
		res:		Set resample resolution in seconds for data, by default res=None -
					no resampling, res=0.05 for evenly spaced 20Hz sampling.
		Ab:			Angle to aberate X and Y components of the data by, in degrees.
					When set to None, the aberation angle will be found automatically.
		DetectGaps:	Largest data gap size (in hours) to interpolate over, 
					if DetectGaps=None then all gaps will be interpolated over,
					otherwise gaps will be filled with NaN.
					
					
	Returns:
		np.recarray of MAG data
	
	'''
	fname='{:08d}.bin'.format(Date)
	if Minute == True:
		path = Globals.MessPath+'MAG/Binary/MSO/Minute/'
	else:
		path = Globals.MessPath+'MAG/Binary/MSO/Full/'

	

	dtype = [('Date','int32'),('ut','float32'),
			('Xmso','float32'),('Ymso','float32'),('Zmso','float32'),
			('Xmsm','float32'),('Ymsm','float32'),('Zmsm','float32'),
			('Bx','float32'),('By','float32'),('Bz','float32')]	
	
	if os.path.isfile(path+fname) == False:
		out = np.recarray(0,dtype=dtype)
		return out

	data = RT.ReadRecarray(path+fname,dtype)

	if Ab is None:
		tmp = GetAberrationAngle(Date)
		Ab = tmp.Angle
	
	if Ab != 0.0:
		#rotate spacecraft position into aberrated coords	
		data.Xmsm,data.Ymsm = RotTrans(data.Xmsm,data.Ymsm,Ab*np.pi/180.0)
		data.Xmso,data.Ymso = RotTrans(data.Xmso,data.Ymso,Ab*np.pi/180.0)
		#rotate bx,by into aberrated coordinate system
		data.Bx,data.By = RotTrans(data.Bx,data.By,Ab*np.pi/180.0)
	

	if res != None:
		UTo = np.array(data.ut)
		
		length=np.int32(86400/res)
		newdata = np.recarray(length,dtype=dtype)
		
		ntags = np.size(data.dtype.names)
		newdata.ut=24*np.arange(length,dtype='float32')/length
		newdata.Date = Date
		for i in range(2,ntags):
			f=InterpolatedUnivariateSpline(data.ut,data[data.dtype.names[i]])
			newdata[newdata.dtype.names[i]]=f(newdata.ut)

		if DetectGaps != None:
			#set Detect gaps to the largest number of seconds gap (5s is used elsewhere)
			MaxUTGapHr = DetectGaps/3600.0
			bad = np.zeros(length,dtype='bool')
			for i in range(0,UTo.size-1):
				if (UTo[i+1]-UTo[i]) > MaxUTGapHr:
					b=np.where((newdata.ut > UTo[i]) & ( newdata.ut <  UTo[i+1]))[0]
					bad[b] = True
			
			baddata = np.where(bad)[0]
			dtags = ['Bx','By','Bz']
			for i in range(0,6):
				if dtags[i] in data.dtype.names:
					newdata[dtags[i]][baddata] = np.float32(np.nan)
			
		return newdata
	else:
		return data
