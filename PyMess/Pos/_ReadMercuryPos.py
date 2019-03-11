import PyFileIO as pf
from .. import Globals

def _ReadMercuryPos():
	'''
	Reads the file which stored Mercury's orbital position in HCI
	coordinates (AU) from 20080101 to 20150431.
	'''
	
	fname = Globals.ModulePath +'/__data/MercuryPos.dat'
	data = pf.ReadASCIIData(fname,True,dtype=[('Date','int32'),('x','float32'),('y','float32'),('z','float32'),('r','float32')])
	
	return data
