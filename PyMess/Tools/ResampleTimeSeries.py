import numpy as np
from .FillGaps import FillGaps
from .InterpGaps import InterpGaps
from .InsertGaps import InsertGaps

def ResampleTimeSeries(xi,yi,xr,MaxGap,UseSpline=True,AddGaps=False):
	
	x = np.copy(xi)
	y = np.copy(yi)
	
	if AddGaps:
		x,y = InsertGaps(x,y,MaxGap)
	
	if MaxGap == None:
		yn = np.copy(y)
	else:
		yn = FillGaps(x,y,MaxGap,UseSpline)

	yr = InterpGaps(x,yn,xr,UseSpline)
	return yr
