import json
import os

import numpy as np

from .GetData import GetData


_CombinedTypes = ('60H','60He','60He2','60Na','60O','10H')


def _JSONValue(value):
	"""Convert a NumPy value to a standards-compliant JSON value."""
	if isinstance(value,np.ndarray):
		return [_JSONValue(item) for item in value]
	if isinstance(value,(np.floating,float)):
		value = float(value)
		return value if np.isfinite(value) else None
	if isinstance(value,(np.bool_,bool)):
		return bool(value)
	if isinstance(value,(np.integer,int)):
		return int(value)
	if isinstance(value,np.str_):
		return str(value)
	if isinstance(value,np.bytes_):
		return bytes(value).decode('utf-8')
	return value


def ExportJSON(Date,FileName,Type='60H',ut=(0.0,24.0)):
	"""Export combined FIPS data to an indented JSON file.

	Parameters
	==========
	Date : int or two-element array
		One date in yyyymmdd format, or an inclusive [start, end] range.
	FileName : str or path-like
		Output JSON filename.
	Type : str
		Combined product: '60H', '60He', '60He2', '60Na', '60O' or '10H'.
	ut : two-element array
		UT range in hours. For a date range, the values limit the first
		and last dates respectively.

	Returns
	=======
	str
		The output filename.
	"""
	if Type not in _CombinedTypes:
		raise ValueError(
			'Type must be a combined FIPS product: {:s}'.format(
				', '.join(_CombinedTypes)
			)
		)
	if np.size(Date) not in (1,2):
		raise ValueError('Date must be a single date or a two-date range')
	if np.size(ut) != 2:
		raise ValueError('ut must contain a start and stop time')

	data = GetData(Date,ut=ut,Type=Type,Verbose=False)
	fields = data.dtype.names or ()
	records = [
		{name:_JSONValue(record[name]) for name in fields}
		for record in data
	]

	filename = os.fspath(FileName)
	parent = os.path.dirname(os.path.abspath(filename))
	os.makedirs(parent,exist_ok=True)
	with open(filename,'w',encoding='utf-8') as f:
		json.dump(records,f,indent=2,allow_nan=False)
		f.write('\n')
	return filename
