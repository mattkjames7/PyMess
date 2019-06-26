import os
import numpy as np

def ListFiles(start,ReturnNames=False):
	'''
	Should list the files that exist within a folder.
	'''
	
	FileOut = []
	NameOut = []
	for root,dirs,files in os.walk(start,topdown=False,followlinks=True):
		for name in files:
			FileOut.append(root+'/'+name)
			NameOut.append(name)
	
	FileOut = np.array(FileOut)
	NameOut = np.array(NameOut)
	
	if ReturnNames:
		return FileOut,NameOut
	else:
		return FileOut
