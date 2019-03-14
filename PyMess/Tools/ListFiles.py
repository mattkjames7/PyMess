import os

def ListFiles(start,ReturnNames=False):
	'''
	Should list the files that exist within a folder.
	'''
	
	FileOut = []
	NameOut = []
	for root,dirs,files in os.walk(start,topdown=False):
		for name in files:
			FileOut.append(root+name)
			NameOut.append(name)
	
	if ReturnNames:
		return FileOut,NameOut
	else:
		return FileOut
