import numpy as np
from scipy.interpolate import interp1d,InterpolatedUnivariateSpline

def FillGaps(xin,y,MaxGap,UseSpline=True):
	yin = np.copy(y)
	
	n = np.size(xin)
	
	bad = np.where(np.isfinite(yin) == False)[0]
	good = np.where(np.isfinite(yin))[0]

	nb = bad.size
	if nb == n or nb < 1:
		return yin
	
	if bad[0] == 0 and xin[good[0]]-xin[0] <= MaxGap:
		yin[0] = 0.0
		bad = np.where(np.isfinite(yin) == False)[0]
		good = np.where(np.isfinite(yin))[0]
	
	nb = bad.size
	if nb == n or nb < 1:
		return yin
			
	if bad[-1] == n-1 and xin[-1]-xin[good[-1]] <= MaxGap:
		yin[-1] = 0.0
		bad = np.where(np.isfinite(yin) == False)[0]
		good = np.where(np.isfinite(yin))[0]
	
	yout = np.copy(yin)
	diffi =  good[1:]-good[:-1]
	gaps = np.where(diffi > 1)[0]
	GapStart = good[gaps]
	GapEnd = good[gaps] + diffi[gaps]
	nG = GapStart.size

	for i in range(0,nG):
		if xin[GapEnd[i]] - xin[GapStart[i]] <= MaxGap:
			Ginds = np.array([GapStart[i]-1,GapStart[i],GapEnd[i],GapEnd[i]+1])
			use = np.where((Ginds >= 0) & (Ginds < n))[0]
			Ginds = Ginds[use]
			use = np.where(np.isfinite(yin[Ginds]))[0]
			Ginds = Ginds[use]
			if Ginds.size < 4 or UseSpline == False:
				f = interp1d(xin[Ginds],yin[Ginds],'linear')
			else:
				f = InterpolatedUnivariateSpline(xin[Ginds],yin[Ginds])
		
			Binds = np.arange(GapStart[i]+1,GapEnd[i],1)
			yout[Binds] = f(xin[Binds])
	
	return yout
