from .. import Globals
import PyFileIO as pf

def _ReadBSCrossings():
	fname = Globals.ModulePath+'__data/MessBS.dat'
	data = pf.ReadASCIIData(fname)
	return data
