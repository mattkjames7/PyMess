import numpy as np
from .FindPDSFiles import FindPDSFiles
from .ReadPDSMAG import ReadPDSMAG
from ... import Globals
import RecarrayTools as RT
import DateTimeTools as TT
from scipy.interpolate import InterpolatedUnivariateSpline
import os

def _ConvertPDS(PrevData,CurrData,NextData,date):
	#create output path
	binpath = Globals.MessPath+'MAG/Binary/Full/'
	minpath = Globals.MessPath+'MAG/Binary/Minute/'
	if not os.path.isdir(binpath):
		os.system('mkdir -pv '+binpath)
	if not os.path.isdir(minpath):
		os.system('mkdir -pv '+minpath)

	#output file name
	fname = '{:08d}.bin'.format(date)
		
	#first of all, find the records which match the current date
	use = np.where(CurrData.Date == date)[0]
	out = CurrData[use]
	if not PrevData is None:
		usep = np.where(PrevData.Date == date)[0]
		if usep.size > 0:
			out = RT.JoinRecarray(PrevData[usep],out)
	if not NextData is None: 
		usen = np.where(NextData.Date == date)[0]
		if usen.size > 0:
			out = RT.JoinRecarray(out,NextData[usen])
	
	#save the full data
	RT.SaveRecarray(out,binpath+fname)
	
	#now to find the minute average data, which will be calculated
	#using half a minute of the previous days data
	use = np.where((PrevData.Date == TT.MinusDay(date)) & (PrevData.ut >= 24.0 - 1.0/120.0))[0]
	tmp = PrevData[use]
	tmp.ut-=24.0
	out = RT.JoinRecarray(tmp,out)
			
	#now to calculate the averages
	minout = np.recarray(1440,dtype=out.dtype)
	minout.Date = date
	minout.ut = np.arange(1440)/60.0
	tags = ['Bx','By','Bz']
	for j in range(0,1440):
		ut0 = j*1.0/60.0 - 0.5/60.0
		ut1 = j*1.0/60.0 + 0.5/60.0
		
		use = np.where((out.ut >= ut0) & (out.ut < ut1))[0]
		for t in tags:
			minout[t][j] = np.nanmean(out[t][use])
		
	tags = ['Xmso','Ymso','Zmso','Xmsm','Ymsm','Zmsm']
	for t in tags:
		f = InterpolatedUnivariateSpline(out.ut,out[t])
		minout[t] = f(minout.ut)
		
	#save minute data
	RT.SaveRecarray(minout,minpath+fname)	

def ConvertPDSDate(Date):
	#get the file list
	files,dates = FindPDSFiles()
	
	use = np.where(dates == Date)[0]
	usep = np.where(dates == TT.MinusDay(Date))[0]
	usen = np.where(dates == TT.PlusDay(Date))[0]
	if use.size == 0:
		print('No data for date {:d}'.format(Date))
		return
	
	print('Reading '+files[use[0]])
	CurrData = ReadPDSMAG(files[use[0]])
	if usep.size > 0:
		print('Reading '+files[usep[0]])
		PrevData = ReadPDSMAG(files[usep[0]])
	else:
		PrevData = None
	if usen.size > 0:
		print('Reading '+files[usen[0]])
		NextData = ReadPDSMAG(files[usen[0]])
	else:
		NextData = None
	_ConvertPDS(PrevData,CurrData,NextData,Date)

def ConvertPDStoBinary():
	'''
	This routine will search for PDS .TAB files, read them in, and 
	convert them to a more convenient binary format.
	
	'''
	
	#get the file list
	files,dates = FindPDSFiles()
	n = files.size
	
	#create output path
	binpath = Globals.MessPath+'MAG/Binary/Full/'
	minpath = Globals.MessPath+'MAG/Binary/Minute/'
	if not os.path.isdir(binpath):
		os.system('mkdir -pv '+binpath)
	if not os.path.isdir(minpath):
		os.system('mkdir -pv '+minpath)
	
	#loop through files
	#sometimes records from the next day are included in the current 
	#file we could really do with fixing that
	PrevData = None
	CurrData = None
	NextData = None
	for i in range(0,n):
		print('\rConverting file {0} of {1}'.format(i+1,n),end='')
		#read in current data
		if i == 0:
			CurrData = ReadPDSMAG(files[i])
		else:
			CurrData = NextData
		#read in next days data
		if i < n-1:
			NextData = ReadPDSMAG(files[i+1])
		else:
			NextData = None
		
		#output file name
		fname = '{:08d}.bin'.format(dates[i])
			
		#first of all, find the records which match the current date
		use = np.where(CurrData.Date == dates[i])[0]
		out = CurrData[use]
		if not PrevData is None:
			usep = np.where(PrevData.Date == dates[i])[0]
			if usep.size > 0:
				out = RT.JoinRecarray(PrevData[usep],out)
		if not NextData is None: 
			usen = np.where(NextData.Date == dates[i])[0]
			if usen.size > 0:
				out = RT.JoinRecarray(out,NextData[usen])
		
		#save the full data
		RT.SaveRecarray(out,binpath+fname)
		
		#now to find the minute average data, which will be calculated
		#using half a minute of the previous days data
		if not PrevData is None:
			#must check that the previous day is infact the previous day
			if dates[i-1] == TT.MinusDay(dates[i]):
				use = np.where((PrevData.Date == dates[i-1]) & (PrevData.ut >= 24.0 - 1.0/120.0))[0]
				tmp = PrevData[use]
				tmp.ut-=24.0
				out = RT.JoinRecarray(tmp,out)
				
		#now to calculate the averages
		minout = np.recarray(1440,dtype=out.dtype)
		minout.Date = dates[i]
		minout.ut = np.arange(1440)/60.0
		tags = ['Bx','By','Bz']
		for j in range(0,1440):
			ut0 = i*1.0/60.0 - 0.5/60.0
			ut1 = i*1.0/60.0 + 0.5/60.0
			
			use = np.where((out.ut >= ut0) & (out.ut < ut1))[0]
			for t in tags:
				minout[t] = np.nanmean(out[t][use])
			
		tags = ['Xmso','Ymso','Zmso','Xmsm','Ymsm','Zmsm']
		for t in tags:
			f = InterpolatedUnivariateSpline(out.ut,out[t])
			minout[t] = f(minout.ut)
			
		#save minute data
		RT.SaveRecarray(minout,minpath+fname)
		
		
		
		#set PrevData
		PrevData = CurrData
	
	print()
