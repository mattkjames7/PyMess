import numpy as np
import PyFileIO as pf
from .. import Globals
import RecarrayTools as RT
from .ContUT import ContUT

def _ReadBoundaries():
	
	
	#the two file names
	mname = Globals.ModuleData + 'mp_crossings.dat'
	bname = Globals.ModuleData + 'bs_crossings.dat'
	
	#read them in
	dtype = [	('ctype','int8'),
				('Date','int32'),
				('ut','float32'),
				('x','float32'),
				('y','float32'),
				('z','float32'),
				('Source','U1')]
	mdata = pf.ReadASCIIData(mname,Header=False,dtype=dtype)			
	bdata = pf.ReadASCIIData(bname,Header=False,dtype=dtype)			
	
	
	#combine them
	data = RT.JoinRecarray(mdata,bdata)

	#sort the data
	utc = ContUT(data.Date,data.ut)
	srt = np.argsort(utc)
	data = data[srt]
	
	return data
