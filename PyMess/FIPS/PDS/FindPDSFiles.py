from pathlib import Path

from ... import Globals

def FindPDSFiles():
	'''
	Searches the PDS directory within the $MESSENGER_PATH/FIPS directory
	for data files and their PDS4 XML labels. PDS3 FMT files are retained
	as a fallback for legacy ESPEC downloads.
	
	Returns:
		Python dict containing lists of data files.
	
	'''
	startpath = Path(Globals.MessPath) / 'FIPS' / 'PDS'
	
	#list of data products
	Prods = ['edr','cdr','espec','ntp']
	
	#list of file patterns
	patt = ['FIPS_R*EDR*.DAT','FIPS_R*CDR*.TAB','FIPS_ESPEC_*.TAB','FIPS_NTP_*.TAB']
	fmts = ['FIPS_SCAN.FMT','FIPS_SCAN_CDR.FMT','FIPS_ESPEC_DDR.FMT','FIPS_NTP_DDR.FMT']


	#list the outpur dirs too
	outdirs = ['EDR/','CDR/','ESPEC/','NTP/']

	#create output dictionary
	out = {}
	
	#now to find file lists
	for i in range(0,4):
		datafiles = sorted(startpath.rglob(patt[i]))
		legacy = sorted(startpath.rglob(fmts[i]))
		labels = []
		kept_files = []
		for datafile in datafiles:
			label = None
			for suffix in ('.xml', '.XML', '.lblx', '.LBLX'):
				candidate = datafile.with_suffix(suffix)
				if candidate.is_file():
					label = candidate
					break
			if label is None and legacy:
				label = legacy[0]
			if label is not None:
				labels.append(str(label))
				kept_files.append(str(datafile))

		out[Prods[i]] = (labels,kept_files,outdirs[i])
		
	return out
