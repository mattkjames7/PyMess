from .. import Globals
import PyFileIO as pf
import numpy as np

def _ReadOrbits():
	'''
	Reads the Orbits.dat file to return a numpy.ndarray containing the 
	start and end times of the MESSENGER orbits around Mercury.
	'''
	
	dtype = [('Orbit','int32'),('Date','int32',(2,)),('ut','float32',(2,))]
	fname = Globals.ModulePath+'__data/Orbits.dat'

	lines = pf.ReadASCIIFile(fname)
	
	nl = np.size(lines)
	data = np.recarray(nl,dtype=dtype)
	
	for i in range(0,nl):
		s = lines[i].split()
		data[i].Orbit = np.int32(s[0])
		data[i].Date = np.array([s[1],s[3]])
		data[i].ut = np.array([s[2],s[4]])
		
	return data
