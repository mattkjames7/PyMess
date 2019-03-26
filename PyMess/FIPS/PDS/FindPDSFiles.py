import numpy as np
from ... import Globals
from ...Tools.SearchForFile import SearchForFile
from ...Tools.SearchForFilePattern import SearchForFilePattern

def FindPDSFiles():
	'''
	Searches the PDS directory within the $MESSENGER_PATH/FIPS directory
	for data files and fmt files.
	
	Returns:
		Python dict containing lists of data files.
	
	'''
	#pds path
	startpath = Globals.MessPath+'FIPS/PDS/'
	
	#list of data products
	Prods = ['edr','cdr','espec','ntp']
	
	#list of fmt files
	fmts = ['FIPS_SCAN.FMT','FIPS_SCAN_CDR.FMT','FIPS_ESPEC_DDR.FMT','FIPS_NTP_DDR.FMT',]
	
	#list of file patterns
	patt = ['FIPS_R*EDR*.DAT','FIPS_R*CDR*.TAB','FIPS_ESPEC_*.TAB','FIPS_NTP_*.TAB']


	#list the outpur dirs too
	outdirs = ['EDR/','CDR/','ESPEC/','NTP/']

	#create output dictionary
	out = {}
	
	#now to find file lists
	for i in range(0,4):
		#find the fmt file first
		fmtfile = SearchForFile(startpath,fmts[i])
		
		#find the list of data files
		datafiles = SearchForFilePattern(startpath,patt[i])
		
		
		#add to the dictionary
		out[Prods[i]] = (fmtfile[0],datafiles,outdirs[i])
		
	return out
