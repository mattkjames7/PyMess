import numpy as np

def InArray(T,A):
	#T and A must be array like
	n = np.size(T)
	out = np.zeros(n,dtype='bool')
	for i in range(0,n):
		out[i] = T[i] in A
	return out
	
