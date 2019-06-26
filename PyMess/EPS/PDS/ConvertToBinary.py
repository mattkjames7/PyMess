import numpy as np
from .FindPDSFiles import FindPDSFiles
from ...Tools.ReadPDSFile import ReadPDSFile
import RecarrayTools as RT
from ... import Globals
from ...Tools.PDSFMTtodtype import PDSFMTtodtype
import DateTimeTools as TT
import os

edrfields = {	'MET':				'MET',
				'FIPS_SCANTYPE':	'ScanType',
				'PROTON_RATE':		'ProtonRate',}
				
cdrfields = {	'MET':				'MET',
				'TIME':				('Date','ut'),
				'DATA_QUALITY':		'Quality',
				'FIPS_SCANTYPE':	'ScanType',
				'PROTON_DIFFINTENS':'ProtonFlux',}

especfields = {	'INDEX':			'Index',
				'MET':				'MET',
				'H':				'HFlux',
				'HE2':				'He2Flux',
				'HE':				'HeFlux',
				'NA_GROUP':			'NaFlux',
				'O_GROUP':			'OFlux',}
				
ntpfields = {	'START_INDEX':		'StartIndex',
				'STOP_INDEX':		'StopIndex',
				'START_MET':		'StartMET',
				'STOP_MET':			'StopMET',
				'TIME_RESL':		'TimeRes',
				'ION':				'Ion',
				'N':				'n',
				'T':				't',
				'P':				'p',
				'N_ERR':			'nErr',
				'T_ERR':			'tErr',
				'P_ERR':			'pErr',
				'QUAL':				'Quality'}
				

def ConvertToBinary(ConvEDR=True,ConvCDR=True,ConvESPEC=True,ConvNTP=True):
	
	#set the NS path
	nspath = Globals.MessPath+'FIPS/'
	
	#get the lists of files
	nspds = FindPDSFiles()

	#set the fname pattern
	fpatts = ['FIPS-EDR-{:08d}.bin','FIPS-CDR-{:08d}.bin','FIPS-ESPEC-{:08d}.bin','FIPS-NTP-{:08d}.bin']
	
	#list the fields to keep and their new names
	allfields = [edrfields,cdrfields,especfields,ntpfields]
	
	#list the 5 products
	Prods = ['edr','cdr','espec','ntp']

	DateInds = [[6,13],[6,13],[11,18],[9,16]]

	ConvList = [ConvEDR,ConvCDR,ConvESPEC,ConvNTP]

	#now loop through converting each product
	for i in range(0,4):
		print('Converting Product: {:s} ({:d}/{:d})'.format(Prods[i],i+1,4))
		if ConvList[i]:
			fmt,files,outdir = nspds[Prods[i]]
			field = allfields[i]
			
			_ConvBinary(fmt,files,outdir,fpatts[i],field,DateInds[i])
		
		
def _NewDtype(pdsdata,fields):
	
	oldfields = list(fields.keys())
	
	newdtype = []
	for f in oldfields:
		sh = pdsdata[f].shape
		if isinstance(fields[f],tuple):
			#this is some date and or time
			if len(fields[f]) == 2:
				newdtype.append(('Date','>i4'))
				newdtype.append(('ut','>f4'))
			elif fields[f][0] == 'Date':	
				newdtype.append(('Date','>i4'))
			else:
				newdtype.append(('ut','>f4'))
		else:
			if len(sh) == 1:
				tmp = (fields[f],pdsdata[f].dtype.str)
			else:
				tmp = (fields[f],pdsdata[f].dtype.str,pdsdata[f].shape[1:])
			newdtype.append(tmp)
	return newdtype
		
		

def _ConvBinary(fmt,files,outdir,fpatt,fields,DateInds):
	#set the output folder
	outpath = Globals.MessPath+'FIPS/'+outdir
	
	if not os.path.isdir(outpath):
		os.system('mkdir -pv '+outpath)
	#get fmt data
	fmtdata = PDSFMTtodtype(fmt)
	
	
	oldfields = list(fields.keys())
	newfields = [fields[f] for f in oldfields]

	
	#loop through files
	nf = np.size(files)
	for i in range(0,nf):
		
		
		#get the date from the file name
		fsplit = files[i].split('/')
		flast = fsplit[-1]
		datestr = flast[DateInds[0]:DateInds[1]+1]
		year = np.int32(datestr[:4])
		doy = np.int32(datestr[4:7])
		Date = TT.DayNotoDate(year,doy)
		
		#read the file first
		data,_ = ReadPDSFile(files[i],fmtdata)
		
		#get the new dtype if needed
		if i == 0:
			dtype = _NewDtype(data,fields)
			print('dtype: ',dtype)
			print(data.dtype)
		print('\rConverting file {:d} of {:d}'.format(i+1,nf),end='')
		#get the output recarray
		out = np.recarray(data.size,dtype=dtype)
		
		#move data to new recarray
		for f in oldfields:
			
			
			if isinstance(fields[f],tuple):
				#probably a date, time or date and time combination
				if len(fields[f]) == 2:
					x = data[f][0]
					out.Date = [TT.DayNotoDate(np.int32(x[0:4]),np.int32(x[5:8])) for x in data[f]]
					out.ut = [np.float32(x[9:11])+np.float32(x[12:14])/60.0+np.float32(x[15:])/3600.0 for x in data[f]]
				elif len(fields[f]) == 1 and fields[f] == 'Date':
					out.Date = [np.int32(x[0:4]+x[5:7]+x[8:10]) for x in data[f]]
				elif len(fields[f]) == 1 and fields[f] == 'ut':
					out.ut = [np.float32(x[0:2]) + np.float32(x[3:5])/60.0 + np.float32(x[6:])/3600.0 for x in data[f]]

			else:
				out[fields[f]] = data[f]

		#save the file
		fname = outpath + fpatt.format(Date)
		RT.SaveRecarray(out,fname)
		
	print()
	

