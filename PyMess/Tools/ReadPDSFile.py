import numpy as np
from .PDSFMTtodtype import PDSFMTtodtype
import os

def ReadPDSFile(fname,fmt):
	'''
	Will attempt to read a PDS data file given the PDS fmt.
	
	Inputs:
		fname: file name of PDS data file.
		fmt: file name of the corresponding .fmt file, or a tuple 
			containing the output of PDSFMTtodtype (this option saves
			parsing the .fmt file every time we read a data file).
	
	Returns:
		data,dtype
		
		data: numpy.recarray
		dtype: list of numpy dtypes for the numpy.recarray
	'''
	if isinstance(fmt,str):
		#can either input the string with the path tot he format file
		fmt = PDSFMTtodtype(fmt)
	else:
		#or just provide a tuple with the results of PDSFMTtodtype
		pass
		
	#either read ascii or binary file
	if fmt[-1] == 'ASCII':
		data,dtype = ReadPDSASCII(fname,fmt)
	else:
		data,dtype = ReadPDSBinary(fname,fmt)
		
	return data,dtype
	
def ReadPDSASCII(fname,fmt):
	'''
	Will attempt to read a PDS ASCII data file (usually .tab) given the
	output of PDSFMTtodtype.
	
	Inputs:
		fname: file name of PDS data file.
		fmt: a tuple containing the output of PDSFMTtodtype.
	
	Returns:
		data,dtype
		
		data: numpy.recarray
		dtype: list of numpy dtypes for the numpy.recarray
	'''

	dtype,dtypestr,startbytes,stopbytes,ne,ito,ftype = fmt
	
	f = open(fname,'r')
	lines = f.readlines()
	f.close()
	n = np.size(lines)
	
	#remove headers from file
	use = np.ones(n,dtype='bool')
	for i in range(0,n):
		if lines[i][0] == '#':
			use[i] = False
	use = np.where(use)[0]
	lines = list(np.array(lines)[use])
	
	n = np.size(lines)
	data = np.recarray(n,dtype=dtype)

	ndt = ne.size
	
	good = np.ones(n,dtype='bool')
	for i in range(0,n):
		#for each line do the following
		s = lines[i]
		try:
			for j in range(0,ndt):
			
				#for each data type
				tmp = s[startbytes[j]:stopbytes[j]]
				if ne[j] > 1:
					#split string into array if ne[j] >1 (not scalar)
					#stride = (stopbytes[j]-startbytes[j])/ne[j]
					stride = ito[j]
					if (ne[j]*stride) != (len(tmp)+1):
						stride -= 1
					tmp = [(tmp[p*stride:(p+1)*stride]).replace(',','') for p in range(0,ne[j])]
				tmp = np.array(tmp).astype(dtype[j][1])
				data[dtype[j][0]][i] = tmp
		except:
			#something has gone wrong, maybe there is a line of text
			#at the top of the file or something
			good[i] = False
				
	keep = np.where(good)[0]
	data = data[keep]
	return data,dtype
			
def ReadPDSBinary(fname,fmt):
	'''
	Will attempt to read a PDS binary data file (usually .dat) given the
	output of PDSFMTtodtype.
	
	Inputs:
		fname: file name of PDS data file.
		fmt: a tuple containing the output of PDSFMTtodtype.
	
	Returns:
		data,dtype
		
		data: numpy.recarray
		dtype: list of numpy dtypes for the numpy.recarray
	'''


	dtype,dtypestr,startbytes,stopbytes,ne,ito,ftype = fmt
	dtypesize = stopbytes[-1]
	
	fsize = os.path.getsize(fname)
	n = fsize//dtypesize
	ndt = ne.size
	
	data = np.recarray(n,dtype=dtype)
	
	f = open(fname,'rb')
	for i in range(0,n):
		for j in range(0,ndt):
			if 'U' in dtype[j][1]:
				tmpdt = dtype[j][1].replace('>U','S')
				t = np.fromfile(f,dtype=tmpdt,count=ne[j])[0]
				tmp = t.decode()
			else:
				tmp = np.fromfile(f,dtype=dtype[j][1],count=ne[j])
				if ne[j] == 1:
					try:
						tmp = tmp[0]
					except:
						print(dtype[j])
			data[dtype[j][0]][i] = tmp

	f.close()


	return data,dtype
