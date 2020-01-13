import numpy as np
from .ReadFIPS import ReadFIPS
from .. import Globals
import DateTimeTools as TT
from scipy import stats
from .FitKappaDist import FitKappaDistCts
from ..Tools.InArray import InArray 
import os
import RecarrayTools as RT

def _CalculateProtonEff(Ebins,Tau,Flux,Counts):
	'''
	This should calculate the proton efficiency for a given spectrum by
	comparing the counts and the flux.
	'''
	dOmega = np.pi*1.15
	g = 8.31e-5

	return Counts/(Flux*Ebins*Tau*g*dOmega)


def Combine60sData(StartI=0,StopI=None,Verbose=True,Overwrite=False):
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
	
	#test each date to see if the required files exist
	exists = np.zeros(nd,dtype='bool')
	path = Globals.MessPath + 'FIPS/'
	for i in range(0,nd):
		ee = os.path.isfile(path + 'EDR/' + 'FIPS-EDR-{:08d}.bin'.format(dates[i]))
		ce = os.path.isfile(path + 'CDR/' + 'FIPS-CDR-{:08d}.bin'.format(dates[i]))
		se = os.path.isfile(path + 'ESPEC/' + 'FIPS-ESPEC-{:08d}.bin'.format(dates[i]))
		ne = os.path.isfile(path + 'NTP/' + 'FIPS-NTP-{:08d}.bin'.format(dates[i]))
		exists[i] = ee | ce | se | ne
	use = np.where(exists)[0]
	dates = np.array(dates)[use]
	nd = np.size(dates)
	if StopI is None:
		StopI = nd
	else:
		StopI = np.min([StopI,nd])
		
	#loop through each date
	for i in range(StartI,StopI):
		print('Combining Date {0} of {1} ({2})'.format(i+1,nd,dates[i]),flush=True)
		_Combine60sDateSpecies(dates[i],'H',Verbose,Overwrite)
		_Combine60sDateSpecies(dates[i],'He',Verbose,Overwrite)
		_Combine60sDateSpecies(dates[i],'He2',Verbose,Overwrite)
		_Combine60sDateSpecies(dates[i],'O',Verbose,Overwrite)
		_Combine60sDateSpecies(dates[i],'Na',Verbose,Overwrite)
	
	
def Combine10sData(StartI=0,StopI=None,Verbose=True,Overwrite=False):
	'''
	This routine will combine the EDR,CDR and DDR FIPS data into a 
	single file for each date. Multiple high time resolution spectra 
	will be combined such that the overall resolution is ~10s. It will 
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
	
	#test each date to see if the required files exist
	exists = np.zeros(nd,dtype='bool')
	path = Globals.MessPath + 'FIPS/'
	for i in range(0,nd):
		ee = os.path.isfile(path + 'EDR/' + 'FIPS-EDR-{:08d}.bin'.format(dates[i]))
		ce = os.path.isfile(path + 'CDR/' + 'FIPS-CDR-{:08d}.bin'.format(dates[i]))
		se = os.path.isfile(path + 'ESPEC/' + 'FIPS-ESPEC-{:08d}.bin'.format(dates[i]))
		ne = os.path.isfile(path + 'NTP/' + 'FIPS-NTP-{:08d}.bin'.format(dates[i]))
		exists[i] = ee | ce | se | ne
	use = np.where(exists)[0]
	dates = np.array(dates)[use]
	nd = np.size(dates)
	if StopI is None:
		StopI = nd
	else:
		StopI = np.min([StopI,nd])
				
	#loop through each date
	for i in range(StartI,StopI):
		print('Combining Date {0} of {1} ({2})'.format(i+1,nd,dates[i]),flush=True)
		_Combine10sDateSpecies(dates[i],'H',Verbose,Overwrite)

	
			
def _Combine60sDateSpecies(Date,Species='H',Verbose=True,Overwrite=False):
	'''
	Combines the relevant files for a given species on a given date.
	
	Inputs
	=======
	Date : integer, format: yyyymmdd
	Species: string 'H','He','He2','O','Na'
	
	'''
	
	#use species to calculate some constants
	mass = Globals.Constants.amu * Globals.IonMass.get(Species,Globals.IonMass['H'])
	e = Globals.Constants.e
	g = Globals.Constants.g
	kB = Globals.Constants.kB
	dOmega = Globals.Constants.dOmega
	eqbins0 = Globals.EQBins[0]
	eqbins2 = Globals.EQBins[2]
	if Species == 'He2':
		vbins0 = np.sqrt((2*e*2000.0*eqbins0)/mass)
		vbins2 = np.sqrt((2*e*2000.0*eqbins2)/mass)
	else:
		vbins0 = np.sqrt((e*2000.0*eqbins0)/mass)
		vbins2 = np.sqrt((e*2000.0*eqbins2)/mass)
	
	
	#get output dtype, file name and path
	OutPath = Globals.MessPath+'FIPS/Combined/60s/{:s}/'.format(Species)
	if not os.path.isdir(OutPath):
		os.system('mkdir -pv '+OutPath)
	dtype = Globals.dtype60s
	fname = OutPath + '{:08d}.bin'.format(Date)
	
	if os.path.isfile(fname) and not Overwrite:
		print("File {:s} exists".format(fname))
		return
		
	#read in the four data files (if they exist)
	dS = ReadFIPS(Date,'espec')
	dN = ReadFIPS(Date,'ntp')
	dE = ReadFIPS(Date,'edr')
	dC = ReadFIPS(Date,'cdr')


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
	grouped = np.zeros(dS.size, dtype='bool')
	for i in range(0,nN):
		use = np.where((dS.Index >= StartInd[i]) & (dS.Index <= StopInd[i]))[0]
		grouped[use] = True
	
	#now to group up the rest
	notgrouped = grouped == False
	ng = np.where(notgrouped)[0]
	met = dS.MET[ng]
	ind = dS.Index[ng]

	if ng.size > 0:
		StM = []
		SpM = []
		StI = []
		SpI = []
		i = 0
		while i < ng.size:
			use = np.where((met >= met[i]) & (met <= met[i]+60.0))[0]
			StM.append(met[use[0]])
			SpM.append(met[use[-1]])
		
			StI.append(ind[use[0]])
			SpI.append(ind[use[-1]])
		
			i = use[-1] + 1
			
		StartMET = np.append(StartMET,np.array(StM))
		StopMET = np.append(StopMET,np.array(SpM))
		StartInd = np.append(StartInd,np.array(StI))
		StopInd = np.append(StopInd,np.array(SpI))
		
		srt = np.argsort(StartMET)
		
		StartMET = StartMET[srt]
		StopMET = StopMET[srt]
		StartInd = StartInd[srt]
		StopInd = StopInd[srt]
	
	#now we should have grouped all of the data, time to create the output array
	n = np.size(StartMET)
	out = np.recarray(n,dtype=dtype)

	#save some ion info
	spstr = Species + (3 - (len(Species)))*' '
	out.Ion = spstr
	out.Mass = mass


	#save ut and MET
	met0 = dC.MET[0] - dC.ut[0]*3600.0 #MET at the start of the day
	out.Date = Date
	out.MET = StopMET
	out.ut = (out.MET-met0)/3600.0
	out.StartIndex = StartInd
	out.StopIndex = StopInd

	#set default CDR quality flag
	#Normally 0 = good, 1 = bad, here -1 = not present
	out.CDRQuality[:] = -1
	out.NTPQuality[:] = -1

	#get the appropriate flux
	Flux = dS[Species+'Flux']
	
	#loop through groups
	for i in range(0,n):
		if Verbose:
			print('\rCopying data {:f}%'.format(100.0*(i+1)/n),end='')
		#get the METS from ESPEC first, the rest have to match this!
		useS = np.where((dS.Index >= StartInd[i]) & (dS.Index <= StopInd[i]))[0]
		METS = dS.MET[useS]

		out[i].StartMET = METS[0]
		out[i].StopMET = METS[-1]
		out[i].MET = METS[-1]
		
		#now find the other indices by using the MET list
		useE = np.where(InArray(dE.MET,METS))[0]
		useC = np.where(InArray(dC.MET,METS))[0]

		#useE = np.where((dE.MET >= StartMET[i]) & (dE.MET <= StopMET[i]))[0]
		
		
		#useC = np.where((dC.MET >= StartMET[i]) & (dC.MET <= StopMET[i]))[0]
		useN = np.where(dN.StartIndex == StartInd[i])[0]

		#get NSpec
		out[i].NSpec = useS.size
		
		#set E/Q and V bins
		if useE.size == 0:
			out[i].ScanType = -1
			out[i].EQBins = eqbins0
			out[i].Tau = 0.095
		else:
			out[i].ScanType = stats.mode(dE[useE].ScanType)[0][0]
			if out[i].ScanType == 0:
				out[i].EQBins = eqbins0
				out[i].VBins = vbins0/1000.0
				out[i].Tau = 0.095
			else:
				out[i].EQBins = eqbins2
				out[i].VBins = vbins2/1000.0
				out[i].Tau = 0.005
			
		
		#copy counts across,summing over spectra (proton counts only here)
		if useE.size > 0 and Species == 'H':
			out[i].Counts = np.sum(dE.ProtonRate[useE],0)
		else:
			out[i].Counts[:] = 0
		
		#now to move the fluxes over from ESPEC
		if useS.size > 0:
			out[i].Flux = np.nanmean(Flux[useS],0)

			#calculate PSD
			out[i].PSD = out[i].Flux*(mass/(out[i].VBins**2)) * (10.0/e)
		
		#save the quality flags
		if useC.size > 0 and Species == 'H':
			out[i].CDRQuality[:useC.size] = dC[useC].Quality
		
		
		#input NTP values if they exist
		out.HasNTP[i] = False
		out.n[i] = np.nan
		out.t[i] = np.nan
		out.p[i] = np.nan
		if useN.size > 0 and Species == 'H':
			#currently this only exists for H
			out.n[i] = dN[useN[0]].n
			out.t[i] = dN[useN[0]].t
			out.p[i] = dN[useN[0]].p
			out.HasNTP[i] = True
			out.NTPQuality[i] = dN[useN[0]].Quality
	if Verbose:
		print()
	
	#This following bit will only work for protons currently, for all other ions Eff = 1
	if Species == 'H':
		#calculate efficiencies
		Tau2 = np.array([5]*52 + [0]*12)/1000.0
		Tau0 = np.array([95]*60 + [0]*4)/1000.0	
		Eff = np.zeros((n,64),dtype='float32')
		for i in range(0,n):
			if Verbose:
				print('\rCalculating Efficiencies {:f}%'.format(100.0*(i+1)/n),end='')
			if out[i].ScanType == 0:
				Ebins = eqbins0
				Tau = Tau0
			else:
				Ebins = eqbins2
				Tau = Tau2		
			zero = np.where(out[i].Counts == 0)[0]
			Eff[i] = _CalculateProtonEff(Ebins,Tau,out[i].Flux,out[i].Counts)
			Eff[i][zero] = np.nan
		
		if np.size(Eff.shape) == 2:
			Eff = np.nanmean(Eff,0)
			Eff[np.isfinite(Eff) == False] = np.nan
	else:
		Tau2 = np.array([5]*52 + [0]*12)/1000.0
		Tau0 = np.array([95]*60 + [0]*4)/1000.0	
		Eff = np.zeros((n,64),dtype='float32')
		for i in range(0,n):
			if Verbose:
				print('\rCalculating Efficiencies {:f}%'.format(100.0*(i+1)/n),end='')
			if out[i].ScanType == 0:
				Ebins = eqbins0
				Tau = Tau0
			else:
				Ebins = eqbins2
				Tau = Tau2		
			zero = np.where(out[i].Counts == 0)[0]
			Eff[i] = Tau*1.0
			Eff[i][zero] = np.nan
		if np.size(Eff.shape) == 2:
			Eff = np.nanmean(Eff,0)
			Eff[np.isfinite(Eff) == False] = np.nan
	if Verbose:
		print()
	
	if Species == 'H':
		#attempt to refit the spectrum with a kappa distribution
		for i in range(0,n):
			if Verbose:
				print('\rRefitting Spectra {:f}%'.format(100.0*(i+1)/n),end='')
			#save efficiency
			out[i].Efficiency[:] = Eff
			

			#set starting guess for n and T based on original fits if they exist
			if np.isnan(out[i].n):
				n0 = 2.0e6
				T0 = 10.0e6
			else:
				n0 = out[i].n*1e6
				T0 = out[i].t*1e6

			#now try fitting
			nTK = FitKappaDistCts(out.VBins[i]*1000.0,out.Counts[i],n0,T0,dOmega,mass,Eff,out[i].NSpec,out[i].Tau,g)
			#check that the values are all positive at least
			if nTK[0] > 0 and nTK[1] > 0 and nTK[2] > 0:
				out[i].nk = nTK[0]/1e6
				out[i].tk = nTK[1]/1e6
				out[i].k = nTK[2]
				out[i].pk = nTK[0]*kB*nTK[1]*1e9
			else:
				out[i].nk = np.nan
				out[i].tk = np.nan
				out[i].k = np.nan
				out[i].pk = np.nan

		if Verbose:
			print()
	if out.size > 0:
		RT.SaveRecarray(out,fname)	
	return out
					
def _Combine10sDateSpecies(Date,Species='H',Verbose=True,Overwrite=False):
	'''
	Combines the relevant files for a given species on a given date.
	
	Inputs
	=======
	Date : integer, format: yyyymmdd
	Species: string 'H','He','He2','O','Na'
	
	'''
	
	#use species to calculate some constants
	mass = Globals.Constants.amu * Globals.IonMass.get(Species,Globals.IonMass['H'])
	e = Globals.Constants.e
	g = Globals.Constants.g
	kB = Globals.Constants.kB
	dOmega = Globals.Constants.dOmega
	eqbins0 = Globals.EQBins[0]
	eqbins2 = Globals.EQBins[2]
	if Species == 'He2':
		vbins0 = np.sqrt((2*e*2000.0*eqbins0)/mass)
		vbins2 = np.sqrt((2*e*2000.0*eqbins2)/mass)
	else:
		vbins0 = np.sqrt((e*2000.0*eqbins0)/mass)
		vbins2 = np.sqrt((e*2000.0*eqbins2)/mass)
	
	
	#get output dtype, file name and path
	OutPath = Globals.MessPath+'FIPS/Combined/10s/{:s}/'.format(Species)
	if not os.path.isdir(OutPath):
		os.system('mkdir -pv '+OutPath)
	dtype = Globals.dtype10s
	fname = OutPath + '{:08d}.bin'.format(Date)
	
	if os.path.isfile(fname) and not Overwrite:
		print("File {:s} exists".format(fname))
		return
		
	
	#read in the four data files (if they exist)
	dS = ReadFIPS(Date,'espec')
	dN = ReadFIPS(Date,'ntp')
	dE = ReadFIPS(Date,'edr')
	dC = ReadFIPS(Date,'cdr')


	#check that there are any data points:
	if dE.size == 0 and dC.size == 0 and dS.size == 0 and dN.size == 0:
		return #no data found at all for this date
		
	
	#find number of record using either EDR/CDR (for H) or ESPEC (for everything else)
	if Species == 'H':
		n = dC.size
		MET = dC.MET
		Index = np.arange(dC.size)
	else:
		n = dS.size
		MET = dS.MET
		Index = dS.Index

	#now time to create the output array
	out = np.recarray(n,dtype=dtype)

	#save some ion info
	spstr = Species + (3 - (len(Species)))*' '
	out.Ion = spstr
	out.Mass = mass


	#save ut and MET
	met0 = dC.MET[0] - dC.ut[0]*3600.0 #MET at the start of the day
	out.Date = Date
	out.Index = Index
	out.MET = MET
	out.ut = (out.MET-met0)/3600.0
	
	#set default CDR quality flag
	#Normally 0 = good, 1 = bad, here -1 = not present
	out.CDRQuality[:] = -1
	out.NTPQuality[:] = -1

	#get the appropriate flux
	Flux = dS[Species+'Flux']
	
	#loop through groups
	for i in range(0,n):
		if Verbose:
			print('\rCopying data {:f}%'.format(100.0*(i+1)/n),end='')
		#get the METS from ESPEC first, the rest have to match this!
		if Species == 'H':
			useS = np.where(dS.Index == Index[i])[0]
			useE = np.array([i])
			useC = np.array([i])
		else:
			useS = np.array([i])
			useC = np.where(dC.Index == Index[i])[0]
			useE = useC



		#useC = np.where((dC.MET >= StartMET[i]) & (dC.MET <= StopMET[i]))[0]
		useN = np.where((dN.StartIndex <= Index[i]) & (dN.StopIndex >= Index[i]))[0]

			
		#set E/Q and V bins
		if useE.size == 0:
			out[i].ScanType = -1
			out[i].EQBins = eqbins0
			out[i].Tau = 0.095
		else:
			out[i].ScanType = stats.mode(dE[useE].ScanType)[0][0]
			if out[i].ScanType == 0:
				out[i].EQBins = eqbins0
				out[i].VBins = vbins0/1000.0
				out[i].Tau = 0.095
			else:
				out[i].EQBins = eqbins2
				out[i].VBins = vbins2/1000.0
				out[i].Tau = 0.005
			
		
		#copy counts across,summing over spectra (proton counts only here)
		if useE.size > 0 and Species == 'H':
			out[i].Counts = np.sum(dE.ProtonRate[useE],0)
		else:
			out[i].Counts[:] = 0
		
		#now to move the fluxes over from ESPEC
		if useS.size > 0:
			out[i].Flux = Flux[useS[0]]

			#calculate PSD
			out[i].PSD = out[i].Flux*(mass/(out[i].VBins**2)) * (10.0/e)
		
		#save the quality flags
		if useC.size > 0:
			out[i].CDRQuality = dC[useC[0]].Quality
		
		
		#input NTP values if they exist
		out.HasNTP[i] = False
		out.n[i] = np.nan
		out.t[i] = np.nan
		out.p[i] = np.nan
		if useN.size > 0 and Species == 'H':
			#currently this only exists for H
			out.n[i] = dN[useN[0]].n
			out.t[i] = dN[useN[0]].t
			out.p[i] = dN[useN[0]].p
			out.HasNTP[i] = True
			out.NTPQuality[i] = dN[useN[0]].Quality
	if Verbose:
		print()
	
	#This following bit will only work for protons currently, for all other ions Eff = 1
	if Species == 'H':
		#calculate efficiencies
		Tau2 = np.array([5]*52 + [0]*12)/1000.0
		Tau0 = np.array([95]*60 + [0]*4)/1000.0	
		Eff = np.zeros((n,64),dtype='float32')
		for i in range(0,n):
			if Verbose:
				print('\rCalculating Efficiencies {:f}%'.format(100.0*(i+1)/n),end='')
			if out[i].ScanType == 0:
				Ebins = eqbins0
				Tau = Tau0
			else:
				Ebins = eqbins2
				Tau = Tau2		
			zero = np.where(out[i].Counts == 0)[0]

			Eff[i] = _CalculateProtonEff(Ebins,Tau,out[i].Flux,out[i].Counts)
			nf = np.where(np.isfinite(Eff[i]) == False)[0]
			Eff[i][nf] = np.nan
			Eff[i][zero] = np.nan
		
		if np.size(Eff.shape) == 2:
			Eff = np.nanmean(Eff,0)
			Eff[np.isfinite(Eff) == False] = np.nan
	else:
		Tau2 = np.array([5]*52 + [0]*12)/1000.0
		Tau0 = np.array([95]*60 + [0]*4)/1000.0	
		Eff = np.zeros((n,64),dtype='float32')
		for i in range(0,n):
			if Verbose:
				print('\rCalculating Efficiencies {:f}%'.format(100.0*(i+1)/n),end='')
			if out[i].ScanType == 0:
				Ebins = eqbins0
				Tau = Tau0
			else:
				Ebins = eqbins2
				Tau = Tau2		
			zero = np.where(out[i].Counts == 0)[0]
			nf = np.where(np.isfinite(Eff) == False)[0]
			Eff[i] = Tau*1.0
			Eff[i][zero] = np.nan
			Eff[i][nf] = np.nan
		if np.size(Eff.shape) == 2:
			Eff = np.nanmean(Eff,0)
			Eff[np.isfinite(Eff) == False] = np.nan
	if Verbose:
		print()
	
	if Species == 'H':
		#attempt to refit the spectrum with a kappa distribution
		for i in range(0,n):
			if Verbose:
				print('\rRefitting Spectra {:f}%'.format(100.0*(i+1)/n),end='')
			#save efficiency
			out[i].Efficiency[:] = Eff
			

			#set starting guess for n and T based on original fits if they exist
			if np.isnan(out[i].n):
				n0 = 2.0e6
				T0 = 10.0e6
			else:
				n0 = out[i].n*1e6
				T0 = out[i].t*1e6

			#now try fitting
			nTK = FitKappaDistCts(out.VBins[i]*1000.0,out.Counts[i],n0,T0,dOmega,mass,Eff,1,out[i].Tau,g)
			#check that the values are all positive at least
			if nTK[0] > 0 and nTK[1] > 0 and nTK[2] > 0:
				out[i].nk = nTK[0]/1e6
				out[i].tk = nTK[1]/1e6
				out[i].k = nTK[2]
				out[i].pk = nTK[0]*kB*nTK[1]*1e9
			else:
				out[i].nk = np.nan
				out[i].tk = np.nan
				out[i].k = np.nan
				out[i].pk = np.nan

		if Verbose:
			print()
	if out.size > 0:
		RT.SaveRecarray(out,fname)	
	return out
					
def _Combine60sDate(Date):


	g = 8.31e-5	
	e = 1.6022e-19
	amu = 1.6605e-27
	MassH = 1.007 * amu
	MassHe = 4.0026 * amu
	MassNa = 22.9898 * amu
	MassO = 15.999 * amu
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
	OutPath = Globals.MessPath+'FIPS/Combined/60s/'
	if not os.path.isdir(OutPath):
		os.system('mkdir -pv '+OutPath)
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
	for i in range(0,nN):
		use = np.where((dS.Index >= StartInd[i]) & (dS.Index <= StopInd[i]))[0]
		grouped[use] = True
	
	#now to try to group the remaining data
	met0 = dC.MET[0] - dC.ut[0]/3600.0 #MET at the start of the day
	#loop through the day one minute at a time
	NewStartMET = np.zeros(1440,dtype='float64')
	NewStopMET = np.zeros(1440,dtype='float64')
	NewStartInd = np.zeros(1440,dtype='int32')-1
	NewStopInd = np.zeros(1440,dtype='int32')-1
	for i in range(0,1440):
		NewStartMET[i] = met0 + i*60.0
		NewStopMET[i] = met0 + (i+1)*60.0
		use = np.where((grouped == False) & (dS.MET >= NewStartMET[i]) & (dS.MET <= NewStopMET[i]))[0]
		if use.size > 0:
			NewStartInd[i] = dS.Index[use[0]]
			NewStopInd[i] = dS.Index[use[-1]]
			NewStartMET[i] = dS.MET[use[0]]
			NewStopMET[i] = dS.MET[use[-1]]

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

	#save ut and MET
	out.Date = Date
	out.MET = StopMET
	out.ut = (out.MET-met0)/3600.0
	out.StartIndex = StartInd
	out.StopIndex = StopInd

	
	#loop through groups
	for i in range(0,n):
		print('\rCopying data {:f}%'.format(100.0*(i+1)/n),end='')
		#get the METS from ESPEC first, the rest have to match this!
		useS = np.where((dS.Index >= StartInd[i]) & (dS.Index <= StopInd[i]))[0]
		METS = dS.MET[useS]

		out[i].StartMET = METS[0]
		out[i].StopMET = METS[-1]
		out[i].MET = METS[-1]
		
		#now find the other indices by using the MET list
		useE = np.where(InArray(dE.MET,METS))[0]
		useC = np.where(InArray(dC.MET,METS))[0]

		#useE = np.where((dE.MET >= StartMET[i]) & (dE.MET <= StopMET[i]))[0]
		
		
		#useC = np.where((dC.MET >= StartMET[i]) & (dC.MET <= StopMET[i]))[0]
		useN = np.where(dN.StartIndex == StartInd[i])[0]

		#get NSpec
		out[i].NSpec = useS.size
		
		#set E/Q and V bins
		if useE.size == 0:
			out[i].ScanType = -1
			out[i].EQBins = bins0
			out[i].Tau = 0.095
		else:
			out[i].ScanType = stats.mode(dE[useE].ScanType)[0][0]
			if out[i].ScanType == 0:
				out[i].EQBins = bins0
				out[i].Tau = 0.095
			else:
				out[i].EQBins = bins2
				out[i].Tau = 0.005
			
		for j in range(0,5):
			out[i].VBins[j] = np.sqrt((e*2000.0*out[i].EQBins)/out[i].Mass[j])/1000.0
		
		
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
		out.HasNTP[i,:] = False
		out.n[i,:] = np.nan
		out.t[i,:] = np.nan
		out.p[i,:] = np.nan
		if useN.size > 0:
			#currently this only exists for H
			out.n[i,0] = dN[useN[0]].n
			out.t[i,0] = dN[useN[0]].t
			out.p[i,0] = dN[useN[0]].p
			out.HasNTP[i,0] = True
	print()
	#calculate efficiencies
	Tau2 = np.array([5]*52 + [0]*12)/1000.0
	Tau0 = np.array([95]*60 + [0]*4)/1000.0	
	E_H = []
	for i in range(0,n):
		print('\rCalculating Efficiencies {:f}%'.format(100.0*(i+1)/n),end='')
		if out[i].ScanType == 0:
			Ebins = bins0
			Tau = Tau0
		else:
			Ebins = bins2
			Tau = Tau2		
		zero = np.where(out[i].Counts[0] == 0)[0]
		E_H.append(_CalculateProtonEff(Ebins,Tau,out[i].Flux[0],out[i].Counts[0]))
		E_H[i][zero] = np.nan
	E_H = np.array(E_H)
	if np.size(E_H.shape) == 2:
		E_H = np.nanmean(E_H,0)
		E_H[np.isfinite(E_H) == False] = np.nan
	
	print()
	#attempt to refit the spectrum with a kappa distribution
	for i in range(0,n):
		print('\rRefitting Spectra {:f}%'.format(100.0*(i+1)/n),end='')
		#save efficiency
		out[i].Efficiency[0,:] = E_H
		

		#set starting guess for n and T based on original fits if they exist
		if np.isnan(out[i].n[0]):
			n0 = 2.0e6
			T0 = 10.0e6
		else:
			n0 = out[i].n[0]*1e6
			T0 = out[i].t[0]*1e6

		#now try fitting
		nTK = FitKappaDistCts(out.VBins[i,0]*1000.0,out.Counts[i,0],n0,T0,dOmega,out.Mass[i,0],E_H,out[i].NSpec,out[i].Tau,g)
		#check that the values are all positive at least
		if nTK[0] > 0 and nTK[1] > 0 and nTK[2] > 0:
			out[i].nk[0] = nTK[0]/1e6
			out[i].tk[0] = nTK[1]/1e6
			out[i].k[0] = nTK[2]
			out[i].pk[0] = nTK[0]*k*nTK[1]*1e9
		else:
			out[i].nk[0] = np.nan
			out[i].tk[0] = np.nan
			out[i].k[0] = np.nan
			out[i].pk[0] = np.nan

	print()
	if out.size > 0:
		RT.SaveRecarray(out,fname)
	
	
def _Combine10sDate(Date):
	
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
	OutPath = Globals.MessPath+'FIPS/Combined/10s/'
	dtype = Globals.fips10sdtype
	fname = OutPath + 'FIPS-10s-{:08d}.bin'.format(Date)


	#read in the four data files (if they exist)
	dE = ReadFIPS(Date,'edr')
	dC = ReadFIPS(Date,'cdr')
	dS = ReadFIPS(Date,'espec')
	dN = ReadFIPS(Date,'ntp')

	#check that there are any data points:
	if dE.size == 0 and dC.size == 0 and dS.size == 0 and dN.size == 0:
		return #no data found at all for this date
		
	#now instead of grouping stuff by the NTP values, we treat each
	#ESPEC record separately, so the total number of records is whatever
	#is in the ESPEC file. Hopefully the METs match up with EDR and CDR!
	n = dS.size
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
