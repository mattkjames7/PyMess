import numpy as np
from ... import Globals
from ...Tools.SearchForFile import SearchForFile
from ...Tools.SearchForFilePattern import SearchForFilePattern

def FindPDSFiles():
	'''
	Searches the PDS directory within the $MESSENGER_PATH/NS directory
	for data files and fmt files.
	
	Returns:
		Python dict containing lists of data files.
	
	'''
	#pds path
	startpath = Globals.MessPath+'NS/PDS/'
	
	
	#list of data products
	Prods = ['cts','gab','gcr','spe','ncr']
	
	#list of fmt files
	fmts = ['ns_cdr_counts.fmt','ns_cdr_gab.fmt','ns_cdr_gcr_spectra.fmt','ns_cdr_spectra.fmt','ns_ddr_ncr.fmt']
	
	#list of file patterns
	patt = ['ns_cdr_cts*.dat','ns_cdr_gab*.tab','ns_cdr_gcr*.dat','ns_cdr_spe*.dat','ms_ddr_ncr*tab']


	#list the outpur dirs too
	outdirs = ['CTS/','GAB/','GCR/','SPE/','NCR/']

	#create output dictionary
	out = {}
	
	#now to find file lists
	for i in range(0,5):
		#find the fmt file first
		fmtfile = SearchForFile(startpath,fmts[i])
		
		#find the list of data files
		datafiles = SearchForFilePattern(startpath,patt[i])
		
		
		#add to the dictionary
		out[Prods[i]] = (fmtfile,datafiles,outdirs[i])
		
	return out
