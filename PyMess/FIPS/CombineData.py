import numpy as np
from .ReadFIPS import ReadFIPS
from .. import Globals
import DateTimeTools as TT

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
			
		out[i].VBinsH = np.sqrt((e*2000.0*out[i].EQBins)/massH)
		out[i].VBinsHe2 = np.sqrt((e*2000.0*out[i].EQBins)/massHe)
		out[i].VBinsHe = np.sqrt((e*2000.0*out[i].EQBins)/massHe)
		out[i].VBinsNa = np.sqrt((e*2000.0*out[i].EQBins)/massNa)
		out[i].VBinsO = np.sqrt((e*2000.0*out[i].EQBins)/massO)
		
		
		#copy counts across,summing over spectra (proton counts only here)
		if useE.size > 0:
			out[i].HCounts = np.sum(dE.ProtonRate[useE],0)
			#add heavy ions here possibly
		
		#now to move the fluxes over from ESPEC
		if useS.size > 0:
			out[i].HFlux = np.nanmean(dS[useS].HFlux,0)
			out[i].He2Flux = np.nanmean(dS[useS].He2Flux,0)
			out[i].HeFlux = np.nanmean(dS[useS].HeFlux,0)
			out[i].NaFlux = np.nanmean(dS[useS].NaFlux,0)
			out[i].OFlux = np.nanmean(dS[useS].OFlux,0)
		
			#calculate PSD
			out[i].HPSD = out[i].HFlux * (massH/(out[i].VBinsH**2)) * (10.0/e)
			out[i].He2PSD = out[i].He2Flux * (massHe2/(out[i].VBinsHe2**2)) * (10.0/e)
			out[i].HePSD = out[i].HeFlux * (massHe/(out[i].VBinsHe**2)) * (10.0/e)
			out[i].NaPSD = out[i].NaFlux * (massNa/(out[i].VBinsNa**2)) * (10.0/e)
			out[i].OPSD = out[i].OFlux * (massO/(out[i].VBinsO**2)) * (10.0/e)

		
		
		
		#input NTP values if they exist
		out[i].HasNTP[:] = False
		out[i].nH = np.nan
		out[i].tH = np.nan
		out[i].pH = np.nan
		out[i].nHe2 = np.nan
		out[i].tHe2 = np.nan
		out[i].pHe2 = np.nan
		out[i].nHe = np.nan
		out[i].tHe = np.nan
		out[i].pHe = np.nan
		out[i].nNa = np.nan
		out[i].tNa = np.nan
		out[i].pNa = np.nan
		out[i].nO = np.nan
		out[i].tO = np.nan
		out[i].pO = np.nan
		if useN.size > 0:
			#currently this only exists for H
			out[i].nH = dN[useN[0]].n
			out[i].tH = dN[useN[0]].t
			out[i].pH = dN[useN[0]].p
			out[i].HasNTP[0] = True
	
		#attempt to refit the spectrum with a kappa distribution
		

	#calculate efficiencies
