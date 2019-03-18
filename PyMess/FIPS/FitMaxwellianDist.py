import numpy as np
from .MaxwellBoltzmannDist import MaxwellBoltzmannDist,MaxwellBoltzmannDistCts
from scipy.optimize import minimize

def _GetMisfitFunc(v,f,df,mass=1.67212e-27):
		
	def Func(X):
		n,T = X 
		
		fm = MaxwellBoltzmannDist(n,v,T,mass)
		
		lf = np.log10(f)
		lm = np.log10(fm)
		diff = np.sqrt(np.sum(((lf-lm)**2)/df)/f.size)
		
		return diff

	return Func

def FitMaxwellianDist(v,f,Counts,n0,T0,mass=1.67212e-27):
	
	#calculate error bars using Poisson statistics
	bad = np.where(np.isfinite(Counts) == False)[0]
	Counts[bad] = 0.0
	Counts1 = np.copy(Counts)
	Counts1[Counts1 < 1.0] = 1.0
	df = np.sqrt(Counts)/Counts1
	delF = df*f	

	#select only good data to fit to
	good = np.where(np.isfinite(f) & (Counts > 1.0))[0]
	if (good.size < 3.0):
		return -1, -1
	Func = _GetMisfitFunc(v[good],f[good],df[good],mass)
	res = minimize(Func,[n0,T0],method='nelder-mead')
	print(res.success)
	#return n,T fitted
	return res.x

		
def _GetMisfitFuncCts(v,C,dC,dOmega=1.15*np.pi,mass=1.67212e-27,ProtonEff=1.0,nSpec=1.0,Tau=0.095,g=8.31e-5):
		
	def Func(X):
		n,T = X 
		
		Cm = MaxwellBoltzmannDistCts(n,v,T,mass,ProtonEff,dOmega,nSpec,Tau,g)
		
		diff = np.sqrt(np.sum(((C-Cm)**2))/C.size)
		
		return diff

	return Func

def FitMaxwellianDistCts(v,Counts,n0,T0,dOmega=1.15*np.pi,mass=1.67212e-27,ProtonEff=1.0,nSpec=1.0,Tau=0.095,g=8.31e-5):
	
	#calculate error bars using Poisson statistics
	bad = np.where(np.isfinite(Counts) == False)[0]
	Counts[bad] = 0.0
	Counts1 = np.copy(Counts)
	Counts1[Counts1 < 1.0] = 1.0
	dC = np.sqrt(Counts)/Counts1
	delC = dC*Counts	

	#select only good data to fit to
	good = np.where((Counts >= 0.0))[0]
	if (good.size < 3.0):
		return -1, -1
	Func = _GetMisfitFuncCts(v[good],Counts[good],dC[good],dOmega,mass,ProtonEff,nSpec,Tau,g)
	res = minimize(Func,[n0,T0],method='nelder-mead')
	if not res.success:
		return -1,-1
	#return n,T fitted
	return res.x

