import numpy as np
from ... import Globals
from ...Tools.SearchForFile import SearchForFile
from ...Tools.SearchForFilePattern import SearchForFilePattern

def FindPDSFiles():
	'''
	Searches the PDS directory within the $MESSENGER_PATH/EPS directory
	for data files and fmt files.
	
	The products which will be converted are:
		EPS_SCAN_SPECTRA (CDR)
		EPS_SUMMARY_SPECTRA (CDR)
		EPS_HIRES_SPECTRA (CDR)
		EPS_LORES_SPECTRA (CDR)
		EPS_PA_DAILY_SPECTROGRAM (DDR)
		EPS_PA_VALUES (DDR)
		
	Returns:
		Python dict containing lists of data files.
	
	'''
	#pds path
	startpath = Globals.MessPath+'EPS/PDS/'
	
	#list of data products
	Prods = ['cdr_hi','cdr_lo','cdr_scan','cdr_summary','ddr_spec','ddr_pa']
	
	#list of fmt files
	fmts = ['EPS_HIRES_CDR.FMT','EPS_LORES_CDR.FMT','EPS_SCAN_CDR.FMT','EPS_SUM_CDR.FMT','EPS_PASD_NUMERIC_DDR.FMT','EPS_PITCH_ANGLES.FMT']
	
	#list of file patterns
	patt = ['EPSH_R*CDR_V*.TAB','EPSL_R*CDR_V*.TAB','EPSS_R*CDR_V*.TAB','EPSS_S*CDR_V*.TAB','EPS_PASD_NUMERIC_*_DDR_V*.TAB','EPSP_A*DDR_V*.TAB']


	#list the outpur dirs too
	outdirs = ['CDR_HI/','CDR_LO/','CDR_SCAN/','CDR_SUMMARY/','DDR_SPEC/','DDR_PA/']

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
