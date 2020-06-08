import numpy as np
from scipy.interpolate import InterpolatedUnivariateSpline
from scipy.interpolate import interp1d

def InterpGaps(x,y,newx,Spline=True):
	
	nx = np.size(x)
	finy = np.isfinite(y)
	
	newy = np.zeros(np.size(newx),dtype='float64')
	newy.fill(np.nan)
	
	st=-1
	ngd=0
	for i in range(0,nx):
		if finy[i]:
			if st == -1:
				st=i
		else:
			if st != -1:
				if ngd == 0:
					Xi0 = np.array([st])
					Xi1 = np.array([i-1])
				else:
					Xi0 = np.append(Xi0,st)
					Xi1 = np.append(Xi1,i-1)	
				st=-1
				ngd+=1
	if st != -1:
		if ngd == 0:
			Xi0 = np.array([st])
			Xi1 = np.array([nx-1])
		else:
			Xi0 = np.append(Xi0,st)
			Xi1 = np.append(Xi1,nx-1)	
		st=-1
		ngd+=1
	if ngd == 0:
		return newy 
	X0 = x[Xi0]
	X1 = x[Xi1]
	for i in range(0,ngd):
		use = np.where((x >= X0[i]) & (x <= X1[i]))[0]
		usenew = np.where((newx >= X0[i]) & (newx <= X1[i]))[0]
		if use.size > 3 and usenew.size > 0 and Spline:
			f = InterpolatedUnivariateSpline(x[use],y[use])
			newy[usenew] = f(newx[usenew])
		elif use.size > 1 and usenew.size > 0:
			f = interp1d(x[use],y[use])
			newy[usenew] = f(newx[usenew])

	return newy
