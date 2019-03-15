import os
import numpy as np

def ListDirectories(start,ReturnNames=False):
	'''
	Should list the files that exist within a folder.
	'''
	
	DirOut = []
	NameOut = []
	for root,dirs,files in os.walk(start,topdown=False):
		for name in dirs:
			DirOut.append(root+'/'+name)
			NameOut.append(name)
	
	DirOut = np.array(DirOut)
	NameOut = np.array(NameOut)
	
	if ReturnNames:
		return DirOut,NameOut
	else:
		return DirOut
