from ... import Globals
import subprocess
import numpy as np
import DateTimeTools as TT

def FindPDSFiles():
	'''
	This function will search the MESSENGER_PATH/MAG/PDS directory for
	*.TAB files and list them along with their dates.
	'''
	
	cmd = 'find '+Globals.MessPath+'/MAG/PDS/ -name "*.TAB"'
	output = subprocess.Popen(cmd,shell=True,stdout=subprocess.PIPE).communicate()[0]
	files = output.decode().split()
	files = np.array(files)
	files.sort()
	
	datesub = [(x.split('/')[-1])[9:14] for x in files]
	years = np.array([2000 + np.int32(x[:2]) for x in datesub])
	doys = np.array([np.int32(x[2:]) for x in datesub])
	
	dates = np.array([TT.DayNotoDate(years[i],doys[i]) for i in range(0,years.size)],dtype='int32')
	
	return files,dates
	
	
