import numpy as np
from ._ReadMSM import _ReadMSM
from . import MagGlobals
from ..Tools.RotTrans import RotTrans
from scipy.interpolate import InterpolatedUnivariateSpline

def _MPN(Date,Minute=False):
	from ..Magnetopause.MSMtoMPN import MSMtoMPN
	from ..Magnetopause.NearestMPPoint import NearestMP3d
	from ..Magnetopause.MPNormal import MPNormal

	'''
	This procedure should return magnetometer data rotated into 
	a magnetopause normal coordinate system based on the Shue et al
	model.
	
	Inputs:
		Date: 32-bit integer containing the date with the format 
			yyyymmdd.
		Minute: Set to True to use minute resolution data, or False for
			full time resolution data.
		res: Tells the function to resample the MAG data to this time
			resolution in seconds.
		Rsm: Subsolar radius of the magnetopause (usually 1.42 on average)
		Ab: Aberration angle in degrees, set to None to calculate 
			automatically.

			
	Returns:
		numpy.recarray
	'''	
	#read minute data first
	MinData = _ReadMSM(Date,Minute=True,res=None,Ab=None,DetectGaps=None)
	
	#if minute == True then use imported function
	if Minute == True:
		BN,BM,BL,pN,pM,pL,xMP,yMP,zMP,nx,ny,nz = MSMtoMPN(MinData.Bx,MinData.By,MinData.Bz,MinData.Xmsm,MinData.Ymsm,MinData.Zmsm,True)
		ut = MinData.ut
		utc = MinData.utc
		Xmsm = MinData.Xmsm
		Ymsm = MinData.Ymsm
		Zmsm = MinData.Zmsm
	#otherwise, use the minute position to get an array of normals and magnetopause positions, then interpolat for the full data
	else:
		txMP,tyMP,tzMP = NearestMP3d(MinData.Xmsm,MinData.Ymsm,MinData.Zmsm)
		tnx,tny,tnz = MPNormal(txMP,tyMP,tzMP)
		
		FullData = _ReadMSM(Date,Minute=False,res=None,Ab=None,DetectGaps=None)
		
		gd = np.where(np.isfinite(tnx) & np.isfinite(tny) & np.isfinite(tnz))[0]
		gdMP = np.where(np.isfinite(txMP) & np.isfinite(tyMP) & np.isfinite(tzMP))[0] 
		
		if gd.size > 3  and gdMP.size > 4:
			f = InterpolatedUnivariateSpline(MinData.ut[gdMP],txMP[gdMP])
			xMP = f(FullData.ut)
			f = InterpolatedUnivariateSpline(MinData.ut[gdMP],tyMP[gdMP])
			yMP = f(FullData.ut)
			f = InterpolatedUnivariateSpline(MinData.ut[gdMP],tzMP[gdMP])
			zMP = f(FullData.ut)

			f = InterpolatedUnivariateSpline(MinData.ut[gd],tnx[gd])
			nx = f(FullData.ut)
			f = InterpolatedUnivariateSpline(MinData.ut[gd],tny[gd])
			ny = f(FullData.ut)
			f = InterpolatedUnivariateSpline(MinData.ut[gd],tnz[gd])
			nz = f(FullData.ut)
			
			
			#now rotate full data
			theta1 = np.arctan2(ny,nx)
		
			px_,pM = RotTrans(FullData.Xmsm,FullData.Ymsm,-theta1)
			Bx_,BM = RotTrans(FullData.Bx,FullData.By,-theta1)	
			
			theta2 = np.arctan2(nz,np.sqrt(nx**2 + ny**2))
			
			pN,pL = RotTrans(px_,FullData.Zmsm,-theta2)
			BN,BL = RotTrans(Bx_,FullData.Bz,-theta2)


			ut = FullData.ut
			utc = FullData.utc
			Xmsm = FullData.Xmsm
			Ymsm = FullData.Ymsm
			Zmsm = FullData.Zmsm		
		else:
			ut = np.array([])
			
	n = np.size(ut)
	dtype = MagGlobals.dtypes['MPN']
	
	data = np.recarray(n,dtype=dtype)
	if n == 0:
		return data
	
	data.ut = ut
	data.BN = BN
	data.BM = BM
	data.BL = BL
	data.Xmsm = Xmsm
	data.Ymsm = Ymsm
	data.Zmsm = Zmsm
	data.pN = pN
	data.pM = pM
	data.pL = pL
	data.xMP = xMP
	data.yMP = yMP
	data.zMP = zMP
	data.nx = nx
	data.ny = ny
	data.nz = nz
	data.r = np.sqrt(xMP**2 + yMP**2 + zMP**2)
	data.phi = np.arctan2(zMP,np.abs(yMP))
	data.E = np.arccos(xMP/data.r)*180.0/np.pi*np.sign(yMP)
	
	
	return data
