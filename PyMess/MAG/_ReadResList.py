import numpy as np
import PyFileIO as pf
from .. import Globals
import DateTimeTools as TT

def _ReadResList()
	'''
	This function will return a numpy.recarray which lists the 
	approximate time resolutions of the MAG data between Date0,ut0 and
	Date1,ut1.
	
	
	'''
	fname = Globals.ModulePath+'/__data/MagRes/res_list.dat'
	
	tmp = pf.ReadASCIIData(fname,False,dtype=[('Date0','int32'),('hhmm','int32'),('Res','int32')])
	n = tmp.size
	dtype = [('Date0','int32'),('ut0','float32'),('Date1','int32'),('ut1','int32'),('Res','int32')]
	data = np.recarray(n,dtype=dtype)
	
	ut = TT.HHMMteDec(tmp.hhmm,True,True)
	
	data.Date0 = tmp.Date0
	data.ut0 = ut
	data.Date1[:-1] = tmp.Date0[1:]
	data.Date1[-1] = 99999999
	data.ut1[:-1] = ut[1:]
	data.ut1[-1] = 24.0
	data.Res = tmp.res
	return data


