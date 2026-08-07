import RecarrayTools as RT
import DateTimeTools as TT
from .. import Globals

def _ReadMercuryPos():
	'''
	Reads the file which stored Mercury's orbital position in HCI
	coordinates (AU) from 20080101 to 20150431.
	'''
	#a common dtype used for storing position
	dtype = [	('Date','int32'),
				('ut','float32'),
				('unix','float64'),
				('xHCI','float64'),
				('yHCI','float64'),
				('zHCI','float64'),
				('xIAU_SUN','float64'),
				('yIAU_SUN','float64'),
				('zIAU_SUN','float64'),
				('Rsun','float64'),
				('LatHCI','float32'),
				('LonHCI','float32'),
				('LatIAU_SUN','float32'),
				('LonIAU_SUN','float32')]
	fname = Globals.ModulePath +'/__data/MercuryPosSmall.bin'
	data = RT.ReadRecarray(fname,dtype=dtype)
	data.unix = TT.UnixTime(data.Date,data.ut)
	
	return data
