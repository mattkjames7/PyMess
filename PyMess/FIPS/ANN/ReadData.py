import numpy as np
from ... import Globals
import PyFileIO as pf

def ReadData():
	'''
	Read in the downloaded ASCII file

	'''
	fname = Globals.MessPath + 'FIPS/ANN/FIPSProtonClass.dat'
	
	return pf.ReadASCIIData(fname,Header=True)
