import numpy as np
from ... import Globals
import os

def DownloadData():
	'''
	This will download the data product created in James et al 2020.
	
	'''
	#the URL of the file to download
	url = "https://leicester.figshare.com/ndownloader/articles/11385897/versions/2"

	#output directory
	tmp = Globals.MessPath + 'FIPS/ANN/tmp/'
	out = Globals.MessPath + 'FIPS/ANN/'
	if not os.path.isdir(tmp):
		os.system('mkdir -pv '+tmp)

	#file name
	zipname = tmp + 'FIPSData.zip'
	dataname = 'FIPSProtonClass.dat'

	#the commands to call
	dlcommand = 'wget {:s} -O {:s}'.format(url,zipname)
	uzcommand = 'unzip {:s} -d {:s} {:s}'.format(zipname,out,dataname)
	
	#run the commands
	os.system(dlcommand)
	os.system(uzcommand)
