import fnmatch as fnm
import os as os
import numpy as np

def FileSearch(dirname,fname):
	'''
	Searches for filenames with a given pattern within a single 
	directory.
	
	Inputs:
		dirname: Directory within which the search will be performed.
		fname: Pattern for the file name, can be an exact file name such
			as 'abc.txt' or include wildcards such as 'abc*.txt'.
			
	Returns:
		nump.ndarray of file names
	'''
	if os.path.isdir(dirname) == False:
		return np.array([])
		
	files=np.array(os.listdir(dirname))
	files.sort()
	matches=np.zeros(np.size(files),dtype='bool')
	for i in range(0,np.size(files)):
		if fnm.fnmatch(files[i],fname):
			matches[i]=True
	
	good=np.where(matches == True)[0]
	if np.size(good) == 0:
		return np.array([])
	else:
		return np.array(files[good])
