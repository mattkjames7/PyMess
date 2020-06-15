import numpy as np
from .. import Globals
from ._ReadBoundaries import _ReadBoundaries

def GetBoundaries():
	
	if Globals.Boundaries is None:
		Globals.Boundaries = _ReadBoundaries()
		
	return Globals.Boundaries
