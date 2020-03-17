import numpy as np
import PyFileIO as pf
from .. import Globals

def _ReadMSTimes():
	
	#the file name
	fname = Globals.ModuleData + 'MSTimes.dat'
	
	return pf.ReadASCIIData(fname)
