import numpy as np

def InsertGaps(t,x,MaxGap=120):
	'''
	Inserts NaNs between gaps in time greater than MaxGap so that the 
	plot line has a split.
	
	Inputs:
		t: Time array in hours.
		x: Array of data to be plotted
		MaxGap: Maximum gap size in seconds.
		
	Outputs:
		newt: New time axis with length t.size + number of gaps added
		newx: new data array corresponding to newt
	
	'''
	#convert maxgap from seconds to hours
	mg = MaxGap/3600.0
	
	#locate where gaps should be inserted
	I = np.where((t[1:] - t[:-1]) > mg)[0]
	
	if I.size > 0:
		#add  NaNs where there should be gaps
		newt = np.zeros(t.size+I.size,dtype=t.dtype) + np.nan
		newx = np.zeros(t.size+I.size,dtype=x.dtype) + np.nan

		I = np.concatenate(([-1],I,[t.size-1]))

		for i in range(0,I.size-1):
			newt[i+I[i]+1:i+I[i+1]+1] = t[I[i]+1:I[i+1]+1]
			newx[i+I[i]+1:i+I[i+1]+1] = x[I[i]+1:I[i+1]+1]
			if i > 0:
				newt[i+I[i]] = 0.5*(t[I[i]]+t[I[i]+1])

		return newt,newx
	else:
		#return original arrays
		return np.array(t),np.array(x)
