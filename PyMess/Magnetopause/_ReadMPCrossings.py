from .. import Globals
import PyFileIO as pf

def _ReadMPCrossings():
	fname = Globals.ModulePath+'__data/MessMP.dat'
	data = pf.ReadASCIIData(fname)
	return data
