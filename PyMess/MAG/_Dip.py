import numpy as np
from ._ReadMSM import _ReadMSM
import KT17 as kt17
from ..Pos.GetAberrationAngle import GetAberrationAngle
from ._MSM2Dipolar import _MSM2Dipolar
from ..Pos.GetMercuryPos import GetMercuryPos
from . import MagGlobals

def _Dip(Date,Minute=False):
	'''
	This procedure should return magnetometer data rotated into 
	a coordinate system useful for studying waves, with components in
	the poloidal, toroidal and parallel directions.
	
	Inputs:
		Date: 32-bit integer containing the date with the format 
			yyyymmdd.
		Minute: Set to True to use minute resolution data, or False for
			full time resolution data.

	Returns:
		numpy.recarray
	'''
	tmp = GetMercuryPos(Date)
	Rau = tmp.r
	ModelParams = [Rau,50.0]
	dtype = MagGlobals.dtypes['Dip']
	
	data = _ReadMSM(Date,Minute=Minute,res=None,Ab=None,DetectGaps=None)
	
	if data.size == 0:
		print('No MSM data found for {:d}'.format(Date))
		return np.recarray(0,dtype=dtype)
	
	t = data.ut
	#data already rotated into aberrated corrdinates
	b1,b2,b3 = data.Bx,data.By,data.Bz
	p1,p2,p3 = data.Xmsm,data.Ymsm,data.Zmsm
	
	#now to get model field vectors in aberrated coordinates 
	#(no need to aberrate them again) including MP check
	m1,m2,m3 = kt17.ModelField(p1,p2,p3,Params=ModelParams)

	#rotate data vectors, then model vectors, then subtract parallel component
	tx,ty,tz = _MSM2Dipolar(b1,b2,b3,m1,m2,m3,p1,p2,p3)
	ttx,tty,ttz = _MSM2Dipolar(m1,m2,m3,m1,m2,m3,p1,p2,p3)
	tz-=ttz

	b1 = tx
	b2 = ty
	b3 = tz

	#returned coordinates will be in aberrated coords
	# Bx,By,Bz == Bpol, Btor, Bpar
	
	out= np.recarray(t.size,dtype=dtype)
	
	out.Date = data.Date
	out.ut = data.ut
	out.utc = data.utc
	out.Bpol = b1
	out.Btor = b2
	out.Bpar = b3
	out.Xmsm = p1
	out.Ymsm = p2
	out.Zmsm = p3
	
	return out
