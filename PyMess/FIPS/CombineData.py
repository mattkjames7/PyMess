import numpy as np
from .ReadFIPS import ReadFIPS
from .. import Globals
import DateTimeTools as TT

def _CalculateProtonEff(Ebins,Tau,Flux,Counts):
	'''
	This should calculate the proton efficiency for a given spectrum by
	comparing the counts and the flux.
	'''
	dOmega = np.pi*1.15
	g = 8.31e-5

	return Counts/(Flux*Ebins*Tau*g*dOmega)


def Combine60sData():
	'''
	This routine will combine the EDR,CDR and DDR FIPS data into a 
	single file for each date. Multiple high time resolution spectra 
	will be combined such that the overall resolution is ~60s. It will 
	also refit the spectra using a kappa distribution function. FIPS 
	plasma moment fits must be treated with caution, as they may not be 
	representative of the actual plasma at times - machine learning work 
	is being used to remove any bad fits.
	
	
	'''
	
	#get list of dates to try from the first  flyby to the last day of 
	#orbital data
	date = 20080820
	dates = []
	while date <= 20150430:
		dates.append(date)
		date = TT.PlusDay(date)
	nd = np.size(dates)
	
	#loop through each date
	for i in range(0,nd):
		print('Combining Date {0} of {1} ({2})'.format(i+1,nd,dates[i]))
		_Combine60sDate(dates[i])
	

def _Combine60sDate(Date):


	g = 8.31e-5	
	e = 1.6022e-19
	amu = 1.6605e-27
	massH = 1.007 * amu
	massHe = 4.0026 * amu
	massNa = 22.9898 * amu
	massO = 15.999 * amu
	dOmega = 1.15*np.pi
	k = 1.38064852e-23
	
	bins2 = np.array([13.577,  12.332,  11.201,  10.174,   9.241,   8.393,
					 7.623,   6.924,   6.289,   5.712,   5.188,   4.713,   4.28 ,
					 3.888,   3.531,   3.207,   2.913,   2.646,   2.403,   2.183,
					 1.983,   1.801,   1.636,   1.485,   1.349,   1.225,   1.113,
					 1.011,   0.918,   0.834,   0.758,   0.688,   0.625,   0.568,
					 0.516,   0.468,   0.426,   0.386,   0.351,   0.319,   0.29 ,
					 0.263,   0.239,   0.217,   0.197,   0.179,   0.163,   0.148,
					 0.134,   0.122,   0.111,   0.1  ,   0.046,   0.046,   0.046,
					 0.046,   0.046,   0.046,   0.046,   0.046,   0.046,   0.046,
					 0.046,   0.046])	

	bins0 = np.array([13.577,  12.332,  11.201,  10.174,   9.241,   8.393,
					 7.623,   6.924,   6.289,   5.712,   5.188,   4.713,   4.28 ,
					 3.888,   3.531,   3.207,   2.913,   2.646,   2.403,   2.183,
					 1.983,   1.801,   1.636,   1.485,   1.349,   1.225,   1.113,
					 1.011,   0.918,   0.834,   0.758,   0.688,   0.625,   0.568,
					 0.516,   0.468,   0.426,   0.386,   0.351,   0.319,   0.29 ,
					 0.263,   0.239,   0.217,   0.197,   0.179,   0.163,   0.148,
					 0.134,   0.122,   0.111,   0.1  ,   0.091,   0.083,   0.075,
					 0.068,   0.062,   0.056,   0.051,   0.046,   0.046,   0.046,
					 0.046,   0.046])	
					 
	
	
	
	#get output dtype, file name and path
	OutPath = Globals.MessPath+'FIPS/Combined/'
	dtype = Globals.fips60sdtype
	fname = OutPath + 'FIPS-60s-{:08d}.bin'.format(Date)

	#read in the four data files (if they exist)
	dE = ReadFIPS(Date,'edr')
	dC = ReadFIPS(Date,'cdr')
	dS = ReadFIPS(Date,'espec')
	dN = ReadFIPS(Date,'ntp')

	#check that there are any data points:
	if dE.size == 0 and dC.size == 0 and dS.size == 0 and dN.size == 0:
		return #no data found at all for this date
		
	#now we need to work out how many records there are - NTP values 
	#don't exist for all data, so using that will cut out other spectra
	#might be a good idea to group up the CDR or EDR data
	StartMET = np.copy(dN.StartMET)
	StopMET = np.copy(dN.StopMET)
	StartInd = np.copy(dN.StartIndex)
	StopInd = np.copy(dN.StopIndex)
	nN = dN.size
	grouped = np.zeros(dS.size)
	for i in range(0,n):
		use = np.where((dS.Index >= StartIndex[i]) & (dS.Index <= StopIndex[i]))[0]
		grouped[use] = True
	
	#now to try to group the remaining data
	met0 = dS.MET[0] - dS.ut[0]/3600.0 #MET at the start of the day
	#loop through the day one minute at a time
	NewStartMET = np.zeros(1440,dtype='float64')
	NewStopMET = np.zeros(1440,dtype='float64')
	NewStartInd = np.zeros(1440,dtype='int32')-1
	NewStopInd = np.zeros(1440,dtype='int32')-1
	for i in range(0,1440):
		NewStartMET[i] = met0 + i*60.0
		NewStopMET[i] = met0 + (i+1)*60.0
		use = np.where((grouped == False) & (dS.MET >= NewStartMET[i]) & (dS.MET <= NewStopMET))[0]
		if use.size > 0:
			NewStartInd[i] = dS.Index[use[0]]
			NewStopInd[i] = dS.Index[use[-1]]

	keep = np.where(NewStartInd > -1)[0]
	
	StartInd = np.append(NewStartInd[keep],StartInd)
	StopInd = np.append(NewStopInd[keep],StopInd)	
	StartMET = np.append(NewStartMET[keep],StartMET)
	StopMET = np.append(NewStopMET[keep],StopMET)
	
	srt = np.argsort(StartMET)
	
	StartMET = StartMET[srt]
	StopMET = StopMET[srt]
	StartInd = StartInd[srt]
	StopInd = StopInd[srt]
	
	#now we should have grouped all of the data, time to create the output array
	n = np.size(StartMET)
	out = np.recarray(n,dtype=dtype)
	
	#save some ion info
	out.Ion[:,0] = 'H  '
	out.Ion[:,1] = 'He2'
	out.Ion[:,2] = 'He '
	out.Ion[:,3] = 'Na '
	out.Ion[:,4] = 'O  '
	out.Mass[:,0] = MassH
	out.Mass[:,1] = MassHe
	out.Mass[:,2] = MassHe
	out.Mass[:,3] = MassNa
	out.Mass[:,4] = MassO
	
	
	#loop through groups
	for i in range(0,n):
		useE = np.where((dE.MET >= StartMET[i]) & (dE.MET < StopMET[i]))[0]
		useC = np.where((dC.MET >= StartMET[i]) & (dC.MET < StopMET[i]))[0]
		useS = np.where((dS.Index >= StartIndex[i]) & (dS.Index <= StopIndex[i]))[0]
		useN = np.where(dN.StartIndex == StartInd[i])[0]
		
		#get NSpec
		out[i].NSpec = useS.size
		
		#set E/Q and V bins
		out[i].ScanType = stats.mode(dE[useE].ScanType)
		if out[i].ScanType == 0:
			out[i].EQBins = bins0
			out[i].Tau = 0.095
		else:
			out[i].EQBins = bins2
			out[i].Tau = 0.005
		
		for j in range(0,5):
			out[i].VBins[j] = np.sqrt((e*2000.0*out[i].EQBins)/out[i].Mass[j])
		
		
		#copy counts across,summing over spectra (proton counts only here)
		if useE.size > 0:
			out[i].Counts[0] = np.sum(dE.ProtonRate[useE],0)
			out[i].Counts[1:5,:] = 0
			#add heavy ions here possibly
		
		#now to move the fluxes over from ESPEC
		if useS.size > 0:
			out[i].Flux[0] = np.nanmean(dS[useS].HFlux,0)
			out[i].Flux[1] = np.nanmean(dS[useS].He2Flux,0)
			out[i].Flux[2] = np.nanmean(dS[useS].HeFlux,0)
			out[i].Flux[3] = np.nanmean(dS[useS].NaFlux,0)
			out[i].Flux[4] = np.nanmean(dS[useS].OFlux,0)
		
			#calculate PSD
			for j in range(0,5):
				out[i].PSD[j] = out[i].Flux[j]*(out[i].Mass[j]/(out[i].VBins[j]**2)) * (10.0/e)
	
		
		
		#input NTP values if they exist
		out[i].HasNTP[:] = False
		out[i].n[:] = np.nan
		out[i].t[:] = np.nan
		out[i].p[:] = np.nan
		if useN.size > 0:
			#currently this only exists for H
			out[i].n[0] = dN[useN[0]].n
			out[i].t[0] = dN[useN[0]].t
			out[i].p[0] = dN[useN[0]].p
			out[i].HasNTP[0] = True
	
	#calculate efficiencies
	Tau2 = np.array([5]*52 + [0]*12)/1000.0
	Tau0 = np.array([95]*60 + [0]*4)/1000.0	
	E_H = []
	for i in range(0,n):
		if out[i].ScanType == 0:
			Ebins = bins0
			Tau = Tau0
		else:
			Ebins = bins2
			Tau = Tau2		
		zero = np.where(out[i].HCounts == 0)[0]
		E_H.append(_CalculateProtonEff(EBins,Tau,out[i].Flux[0],out[i].Counts[0]))
		E_H[i][zero] = np.nan
	E_H = np.array(E_H)
	E_H = np.nanmean(E_H,0)
	
	#attempt to refit the spectrum with a kappa distribution
	for i in range(0,n):
		#save efficiency
		data[i].Efficiency[0,:] = E_H
		

		#set starting guess for n and T based on original fits if they exist
		if np.isnan(out[i].n[0]):
			n0 = 2.0e6
			T0 = 10.0e6
		else:
			n0 = out[i].n[0]*1e6
			T0 = out[i].T[0]*1e6

	
		#now try fitting
		nTK = FitKappaDistCts(out[i].VBins[0],n0,T0,dOmega,out[i].Mass[0],E_H,out[i].NSpec,out[i].Tau,g)
		
		#check that the values are all positive at least
		if nTK[0] > 0 and nTK[1] > 0 and nTK[2] > 0:
			out[i].nk[0] = nTK[0]
			out[i].tk[0] = nTK[1]
			out[i].k[0] = nTK[2]
			out[i].pk[0] = nTK[0]*k*nTK[1]
		else:
			out[i].nk[0] = np.nan
			out[i].tk[0] = np.nan
			out[i].k[0] = np.nan
			out[i].pk[0] = np.nan

	
	return out
