import numpy as np

def PDSFMTtodtype(fname):
	'''
	Reads a PDS .fmt file and attempts to construct a list of numpy
	dtypes for use in a numpy recarray.
	
	Input:
		fname: name and path to the .fmt file.
	
	Returns:
		dtype,dtypestr,startbytes,stopbytes,ne,itemoffset,ftype

		dtype: dtype list compatible with numpy.recarray.
		dtypestr: dtype converted to a string or Python code.
		startbytes: starting byte number for each item within a record.
		stopbytes: last byte corresponding to each item within a record.
		ne: number of elements
		itemoffset: offset between each item
		ftype: 'BINARY' or 'ASCII'	
	'''
	f = open(fname,'r')
	lines = f.readlines()
	f.close()
		
	return TexttoFMT(lines)
	

def TexttoFMT(lines):
	'''
	Converts the text from a .fmt file into a list of numpy dtypes.
	
	Input:
		lines: list or array of strings read from the .fmt file.
		
	Returns:
		dtype,dtypestr,startbytes,stopbytes,ne,itemoffset,ftype

		dtype: dtype list compatible with numpy.recarray.
		dtypestr: dtype converted to a string or Python code.
		startbytes: starting byte number for each item within a record.
		stopbytes: last byte corresponding to each item within a record.
		ne: number of elements
		itemoffset: offset between each item
		ftype: 'BINARY' or 'ASCII'	
	'''
	n = np.size(lines)
	
	#count objects
	no,ObjsTxt = GetObjects(lines)
	
	#work out what each object is
	dtype,dtypestr,startbytes,stopbytes,ne,itemoffset,ftype = GetObjDtypes(no,ObjsTxt)
	
	return dtype,dtypestr,startbytes,stopbytes,ne,itemoffset,ftype
	
def GetObjects(lines):
	'''
	Scans the fmt file contents for a list of the individual objects.
	
	Input:
		lines: list or array of strings read from the .fmt file.
		
	Returns:
		no,Objs
		
		no: number of objects
		Objs: list of string arrays, each of which corresponds to one 
			data item.
	'''
	
	Objs = []
	no = 0
	
	n = np.size(lines)
	os = -1
	for i in range(0,n):
		s = lines[i]
		if s[0:6] == 'OBJECT':
			os = i
		if s[0:10] == 'END_OBJECT':
			Objs.append(lines[os+1:i])
			no += 1
			os = -1
		
	return no,Objs
	
def GetObjDtypes(no,Objs):
	'''
	Reads each object and determines the equivalent numpy data name, 
	type and shape.
	
	Inputs:
		no: integer number of data items.
		Objs: list of strings corresponding to each data object.
		
	Returns:
		dtype,dtypestr,startbytes,stopbytes,ne,itemoffset,ftype
		
		dtype: dtype list compatible with numpy.recarray.
		dtypestr: dtype converted to a string or Python code.
		startbytes: starting byte number for each item within a record.
		stopbytes: last byte corresponding to each item within a record.
		ne: number of elements
		itemoffset: offset between each item
		ftype: 'BINARY' or 'ASCII'
	'''
	ftype = 'BINARY'
	outstr = '['
	dtypeout = []
	startbytes = np.zeros(no,dtype='int32')
	stopbytes = np.zeros(no,dtype='int32')
	ne = np.zeros(no,dtype='int32')
	itemoffset = np.zeros(no,dtype='int32')
	for i in range(0,no):
		nm,dt,sh,b0,b1,its,ito,isascii = GetObjDtype(Objs[i])
		startbytes[i] = b0-1
		stopbytes[i] = b1-1
		ne[i] = its
		itemoffset[i] = ito
		if isascii:
			ftype = 'ASCII'
		if sh == (1,):
			outstr += "('{:s}','{:s}')".format(nm,dt)
			dtypeout.append((nm,dt))
		else:
			outstr += "('{:s}','{:s}',({:d},))".format(nm,dt,sh[0])
			dtypeout.append((nm,dt,sh))
		if i < no-1:
			outstr+=','
	outstr += ']'
	return dtypeout,outstr,startbytes,stopbytes,ne,itemoffset,ftype
	

def GetObjDtype(Obj):
	'''
	Determines the dtype of an individual object.
	
	Input:
		Obj: list or array of strings corresponding to one data item
			from the .fmt file.
		
	Returns:
		name,dtype,shape,b0,b1,items,itemoffset,isascii
		
		name: variable name
		dtype: numpy dtype
		shape: shape tuple of each record
		b0: start byte
		b1: stop byte
		items: number of elements within this record
		itemoffset: offset between each item (I think)
		isascii: bool - whether the file is ascii or binary.
		
	'''
	F,V = GetObjFields(Obj)
	
	
	#get dtype
	dt = np.where(np.array(F) == 'DATA_TYPE')[0]
	dt = V[dt[0]]
	dtype = ConvertDataType(dt)
	
	#set isascii flag
	isascii = 'ASCII' in dt
	
	
	#get bytes
	bt = np.where(np.array(F) == 'BYTES')[0]
	bt = np.int32(V[bt[0]])
	bits = bt*8
	
	#get start byte
	sb = np.where(np.array(F) == 'START_BYTE')[0]
	b0 = np.int32(V[sb[0]])
	b1 = b0 + bt
	
	
	#get number of elements and bytes
	if 'ITEMS' in F:
		it = np.where(np.array(F) == 'ITEMS')[0]
		items = np.int32(V[it[0]])
		itb = np.where(np.array(F) == 'ITEM_BYTES')[0]
		itembytes = np.int32(V[itb[0]])
	else:
		items = 1
		itembytes = bt
		
	if 'ITEM_OFFSET' in F:
		ito = np.where(np.array(F) == 'ITEM_OFFSET')[0]
		itemoffset = np.int32(V[ito[0]])
	else:
		itemoffset = itembytes
	
	#shape is fairly easy
	shape = (items,)
	
	#and the name	
	nm = np.where(np.array(F) == 'NAME')[0]
	name = V[nm[0]]
	
	#get length
	if dtype in ['float','int','uint']:
		if 'ASCII' in dt:
			#in the ASCII case we assume a length:
			if dtype == 'float':
				dtype = dtype+'64'
			else:
				dtype = dtype+'32'
		else:
			#in the binary case we need to work out what size it is in the file
			if items == 1:
				#this is a scalar
				dtype = dtype + '{:d}'.format(bits)
			else:
				#array
				dtype = dtype + '{:d}'.format(itembytes*8)
	elif dtype == 'U':
		dtype += '{:d}'.format(bt)


	
			
		
	return name,dtype,shape,b0,b1,items,itemoffset,isascii

DataTypes = {	'TIME':'U',
				'ASCII_REAL':'float',
				'ASCII_INTEGER':'int',
				'MSB_UNSIGNED_INTEGER':'uint',
				'CHARACTER':'U'}
				
				
					
				
				

def ConvertDataType(intype):
	'''
	Converts the dtype string from the .fmt file to a numpy dtype 
	string.
	
	Input:
		intype: string containing the pds data type
		
	Returns:
		string containing the numpy dtype equivalent
	'''
	global DataTypes
	if intype in DataTypes.keys():
		return DataTypes[intype]
	else:
		return ''
	


def GetObjFields(Obj):
	'''
	Reads a data object and lists the fields contained within, along
	with their values.
	
	Inputs:
		Obj: list or array of strings corresponding to one data item
			from the .fmt file.
			
	Returns:
		Fields,Vals
	'''
	n = np.size(Obj)
	
	#remove Description
	ds0 = -1
	ds1 = -1
	for i in range(0,n):
		s = Obj[i].strip()
		if ds0 > -1 and '"' in s:
			ds1 = i
			break
		if s[0:11] == 'DESCRIPTION':
			ds0 = i

	if ds0 > -1 and ds1 == -1:
		ds1 = ds0

	if ds0 > -1 and ds1 > -1:
		use = np.ones(n,dtype='bool')
		use[ds0:ds1+1] = False
		use = np.where(use)[0]
		Obj = list(np.array(Obj)[use])
	
	#now get list of object fields and values
	n = np.size(Obj)
	Fields = []
	Vals = []
	for i in range(0,n):
		s = Obj[i].strip().split()
		Fields.append(s[0])
		Vals.append(s[-1])
		
	return Fields,Vals
	
	
