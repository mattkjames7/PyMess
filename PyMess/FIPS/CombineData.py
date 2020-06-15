import numpy as np
from .ReadData import ReadData
from .. import Globals
import DateTimeTools as TT
from scipy import stats
from .FitKappaDist import FitKappaDistCts
from ..Tools.InArray import InArray 
import os
import RecarrayTools as RT
from ..Tools.MatchUT import MatchUT
from ..Tools.ContUT import ContUT
from ..Pos.GetRegion import GetRegion 
from ..Pos.GetPosition import GetPosition
from scipy.interpolate import interp1d

def _CalculateProtonEff(Ebins,Tau,Flux,Counts):
	'''
	This should calculate the proton efficiency for a given spectrum by
	comparing the counts and the flux.
	'''
	dOmega = np.pi*1.15
	g = 8.31e-5

	return Counts/(Flux*Ebins*Tau*g*dOmega)


def Combine60sData(StartI=0,StopI=None,Verbose=True,Overwrite=False,DryRun=False,Species=['H','He','He2','Na','O']):
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
		if Verbose:
			print('\rChecking date {0} of {1}'.format(i+1,nd),end='')
		ee = os.path.isfile(path + 'EDR/' + 'FIPS-EDR-{:08d}.bin'.format(dates[i]))
		ce = os.path.isfile(path + 'CDR/' + 'FIPS-CDR-{:08d}.bin'.format(dates[i]))
		se = os.path.isfile(path + 'ESPEC/' + 'FIPS-ESPEC-{:08d}.bin'.format(dates[i]))
		ne = os.path.isfile(path + 'NTP/' + 'FIPS-NTP-{:08d}.bin'.format(dates[i]))
		exists[i] = ee | ce | se | ne
	if Verbose:
		print()
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
		for S in Species:
			print('Combining: '+S)
			_Combine60sDateSpecies(dates[i],S,Verbose,Overwrite,DryRun)
	
	
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

	
			
def _Combine60sDateSpecies(Date,Species='H',Verbose=True,Overwrite=False,DryRun=False):
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
	
	if os.path.isfile(fname) and not Overwrite and not DryRun:
		print("File {:s} exists".format(fname))
		return
		
	#read in the four data files (if they exist)
	dS = ReadData(Date,'espec')
	dN = ReadData(Date,'ntp')
	dE = ReadData(Date,'edr')
	dC = ReadData(Date,'cdr')
	if Species == 'H':
		dA = ReadData(Date,'ann')
	else:
		dA = None

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
	if n == 0:
		print('no data')
		return
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
	
	#continuous ut
	out.utc = ContUT(out.Date,out.ut)
	
	#position
	pos = GetPosition(Date)
	if pos.size > 0:
		fx = interp1d(pos.ut,pos.x,kind='cubic',bounds_error=False,fill_value='extrapolate')
		fy = interp1d(pos.ut,pos.y,kind='cubic',bounds_error=False,fill_value='extrapolate')
		fz = interp1d(pos.ut,pos.z,kind='cubic',bounds_error=False,fill_value='extrapolate')
		out.x = fx(out.ut)
		out.y = fy(out.ut)
		out.z = fz(out.ut)
	else:
		pos.x = np.nan
		pos.y = np.nan
		pos.z = np.nan
		
	#location
	out.Loc = GetRegion(out.Date,out.ut,out.utc,Verbose=False)
	

	#set default CDR quality flag
	#Normally 0 = good, 1 = bad, here -1 = not present
	out.CDRQuality[:] = -1
	out.NTPQuality[:] = -1
	
	#match ut with ANN output and get ANN outputs
	out.Class[:] = -1
	out.SplitClass[:,:] = -1 
	out.Prob[:] = np.nan
	out.SplitProb[:,:] = np.nan
	out.nk[:] = np.nan
	out.tk[:] = np.nan
	out.pk[:] = np.nan
	out.k[:] = np.nan

	if not dA is None:
		if dA.size > 0:
			Imatch,_ = MatchUT(out.ut,dA.ut)
			ngood = np.sum(Imatch > -1)
			if ngood == dA.size:
				if Verbose:
					print('ANN data match')
			elif ngood < dA.size:
				print('WARNING: missing {:d} ANN points'.format(dA.size-ngood))
			else:
				print('WARNING: too many matches, something really bad has happened!')
			for i in range(0,Imatch.size):
				if Imatch[i] > -1:
					out.Class[i] = dA.Class[Imatch[i]]
					out.SplitClass[i] = dA.SplitClass[Imatch[i]]
					out.Prob[i] = dA.Prob[Imatch[i]]
					out.SplitProb[i] = dA.SplitProb[Imatch[i]]
					out.nk[i] = dA.nk[Imatch[i]]
					out.tk[i] = dA.tk[Imatch[i]]
					out.k[i] = dA.K[Imatch[i]]
					out.pk[i] = out.nk[i]*1e6*kB*out.tk[i]*1e6*1e9
		


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
			
			#changed this bit so that fitting only happens if n,T,K haven't already been defined in ANN data
			if np.isnan(out[i].nk):
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
	if out.size > 0 and not DryRun:
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
	dS = ReadData(Date,'espec')
	dN = ReadData(Date,'ntp')
	dE = ReadData(Date,'edr')
	dC = ReadData(Date,'cdr')


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

	#continuous ut
	out.utc = ContUT(out.Date,out.ut)
	
	#position
	pos = GetPosition(Date)
	if pos.size > 0:
		fx = interp1d(pos.ut,pos.x,kind='cubic',bounds_error=False,fill_value='extrapolate')
		fy = interp1d(pos.ut,pos.y,kind='cubic',bounds_error=False,fill_value='extrapolate')
		fz = interp1d(pos.ut,pos.z,kind='cubic',bounds_error=False,fill_value='extrapolate')
		out.x = fx(out.ut)
		out.y = fy(out.ut)
		out.z = fz(out.ut)
	else:
		pos.x = np.nan
		pos.y = np.nan
		pos.z = np.nan
	
	#location
	out.Loc = GetRegion(out.Date,out.ut,out.utc,Verbose=False)
	

	
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
					
