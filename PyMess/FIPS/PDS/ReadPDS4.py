"""Read the PDS4 binary and fixed-width character tables used by FIPS."""

from pathlib import Path
import xml.etree.ElementTree as ET

import numpy as np


_BINARY_TYPES = {
	"UnsignedMSB2": ">u2",
	"UnsignedMSB4": ">u4",
}


def _Name(element):
	return element.tag.rsplit("}", 1)[-1]


def _Child(element, name):
	for child in element:
		if _Name(child) == name:
			return child
	raise ValueError("Missing PDS4 element: {:s}".format(name))


def _Text(element, name):
	return _Child(element, name).text.strip()


def _Table(root):
	for element in root.iter():
		if _Name(element) in ("Table_Binary", "Table_Character"):
			return element
	raise ValueError("The PDS4 label does not contain a supported table")


def _FieldDtype(data_type, length):
	if data_type in _BINARY_TYPES:
		return _BINARY_TYPES[data_type]
	if data_type == "ASCII_Real":
		return ">f8"
	if data_type == "ASCII_Integer":
		return ">i4"
	if data_type.startswith("ASCII_"):
		return ">U{:d}".format(length)
	raise ValueError("Unsupported PDS4 data type: {:s}".format(data_type))


def _Fields(record):
	"""Extract field layout, including fields nested in repeating groups."""
	fields = []
	for element in record:
		kind = _Name(element)
		if kind in ("Field_Binary", "Field_Character"):
			length = int(_Text(element, "field_length"))
			fields.append({
				"name": _Text(element, "name"),
				"dtype": _FieldDtype(_Text(element, "data_type"), length),
				"location": int(_Text(element, "field_location")) - 1,
				"length": length,
				"repetitions": 1,
				"stride": length,
			})
		elif kind in ("Group_Field_Binary", "Group_Field_Character"):
			repetitions = int(_Text(element, "repetitions"))
			group_location = int(_Text(element, "group_location")) - 1
			group_length = int(_Text(element, "group_length"))
			stride = group_length // repetitions
			for child in element:
				if _Name(child) not in ("Field_Binary", "Field_Character"):
					continue
				length = int(_Text(child, "field_length"))
				fields.append({
					"name": _Text(child, "name"),
					"dtype": _FieldDtype(_Text(child, "data_type"), length),
					"location": group_location + int(_Text(child, "field_location")) - 1,
					"length": length,
					"repetitions": repetitions,
					"stride": stride,
				})
	return fields


def _Dtype(fields):
	dtype = []
	for field in fields:
		item = (field["name"], field["dtype"])
		if field["repetitions"] > 1:
			item += ((field["repetitions"],),)
		dtype.append(item)
	return dtype


def _ReadBinary(filename, offset, records, record_length, fields):
	names = []
	formats = []
	offsets = []
	for field in fields:
		if field["stride"] != field["length"]:
			raise ValueError("Strided PDS4 binary groups are not supported")
		names.append(field["name"])
		shape = (field["repetitions"],) if field["repetitions"] > 1 else ()
		formats.append(np.dtype((field["dtype"], shape)))
		offsets.append(field["location"])
	disk_dtype = np.dtype({
		"names": names,
		"formats": formats,
		"offsets": offsets,
		"itemsize": record_length,
	})
	with open(filename, "rb") as handle:
		handle.seek(offset)
		disk_data = np.fromfile(handle, dtype=disk_dtype, count=records)
	data = np.recarray(disk_data.size, dtype=_Dtype(fields))
	for name in names:
		data[name] = disk_data[name]
	return data


def _Value(text, dtype):
	text = text.strip().strip('"')
	if "U" in dtype:
		return text
	return np.array(text).astype(dtype)


def _ReadCharacter(filename, offset, records, record_length, fields):
	data = np.recarray(records, dtype=_Dtype(fields))
	with open(filename, "rb") as handle:
		handle.seek(offset)
		for i in range(records):
			record = handle.read(record_length).decode("ascii")
			if len(record) != record_length:
				raise ValueError("Unexpected end of PDS4 table: {:s}".format(str(filename)))
			for field in fields:
				values = []
				for j in range(field["repetitions"]):
					start = field["location"] + j * field["stride"]
					text = record[start:start + field["length"]]
					values.append(_Value(text, field["dtype"]))
				data[field["name"]][i] = values[0] if len(values) == 1 else values
	return data


def ReadPDS4(label):
	"""Read a FIPS data table using its paired PDS4 XML/LBLX label.

	Returns ``(data, dtype)`` in the same form as the older ``ReadPDSFile``
	utility, allowing the converter to support both PDS3 and PDS4 archives.
	"""
	label = Path(label)
	root = ET.parse(str(label)).getroot()
	file_name = None
	for element in root.iter():
		if _Name(element) == "File":
			file_name = _Text(element, "file_name")
			break
	if file_name is None:
		raise ValueError("No data file is named in {:s}".format(str(label)))

	table = _Table(root)
	offset = int(_Text(table, "offset"))
	records = int(_Text(table, "records"))
	record = _Child(table, "Record_" + ("Binary" if _Name(table) == "Table_Binary" else "Character"))
	record_length = int(_Text(record, "record_length"))
	fields = _Fields(record)
	filename = label.parent / file_name
	if _Name(table) == "Table_Binary":
		data = _ReadBinary(filename, offset, records, record_length, fields)
	else:
		data = _ReadCharacter(filename, offset, records, record_length, fields)
	return data, data.dtype.descr
