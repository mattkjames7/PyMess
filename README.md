# PyMess - soon to be renamed
A Python module for reading the MESSENGER data (or at least some of it)

So far there are some tools for loading and plotting MAG, FIPS and NS data. The 
spacecraft position can also be retrieved/plotted. A list of bow shock (BS) and
magnetopause (MP) crossings based on the work of Winslow et al., 2013 is 
included, which are used to provide a list of times where MESSENGER is in the 
solar wind (SW) and the magnetosheath (MSH).

In future I hope to include EPS and XRS submodules too.

## Installation:

Currently there is no release package on GitHub, nor is there a package 
to PyPI, so the easiest way to install this module is to download this 
repository, or clone it using:
`git clone https://github.com/mattkjames7/PyMess.git`
then to either copy the `PyMess/PyMess` subfolder to your `$PYTHONPATH`, or 
to create your own Python wheel:
`
cd PyMess
python3 setup.py sdist bdist_wheel
pip3 install dist/PyMess-0.0.1-py3-none-any.whl --user
`
which may, or may not work in the code's current state!

After installation, it would be wise to set up the `$MESSENGER_PATH`
environment variable, as this tells the code where to find MESSENGER
data.


##Submodules

1. `FIPS`
2. `MAG`
3. `NS`
4. `Pos`
5. `BowShock`
6. `Magnetopause`
7. `Magnetosheath`
8. `ModelField`
9. `Tools`

### 1. `FIPS` - Fast Imaging Plasma Spectrometer

This module contains routines to read FIPS plasma data. Within the `FIPS`
submodule, there is code to convert the PDS (Planetary Data System) data
to a more convenient format. The PDS data is stored either in ASCII or
binary files. The ASCII files tend to be much larger than necessary, and 
thus take a long time to read, the binary files are organised in records,
which also take a long time to load. The following routines convert both
types to a file format where each variable is stored contiguously within
the file, allowing for fast reading times and smaller files.

#### To convert to binary files:
Run:

`
PyMess.FIPS.PDS.ConvertToBinary()
`

which will scan the `$MESSENGER_PATH/FIPS/PDS` folder for the PDS files.

Another recommended routine combines the new binary files into 1-minute 
resolution binary files:

`
PyMess.FIPS.Combine60sData()
`

In future, there will be a routine to combine the high time resolution 
data also.

#### To load converted data:

To load any of the converted data, use the `PyMess.FIPS.ReadFIPS` 
function, e.g.:

`
data = PyMess.FIPS.ReadFIPS(Date,Type=Type)
`
where `Date` is a 32-bit (or more) integer date in the format yyyymmdd,
and `Type` is a string to say the type of data to load, this string can
be one of the following:
	
	* 'edr' - To load the EDR data
	* 'cdr' - To load the CDR data
	* 'ntp' - To load the DDR NTP data
	* 'espec' - To load the DDR ESPEC data
	* '60' - To load the combined 60s data (default)
	* '10' - To load the combined 10s data

### 2. `MAG` - Magnetometer

This module contains some basic routines to convert, read and plot the
magnetometer data.

#### To convert PDS data:

Download PDS data and extract data to `$MESSENGER_PATH/MAG/PDS`.

Convert the PDS .TAB files using

`PyMess.MAG.PDS.ConvertToBinary()`

which should reduce the size of the dataset from GB to GB.

By default, the magnetometer data used is in MSO coordinates, but we can
also rotate the data into a coordinate system more useful for studying 
ULF waves. In this coordinate system, there is one component parallel to 
the ambient magnetic field; one oriented in the toroidal/azimuthal 
direction (eastward); the third component completes the right-handed set 
and points in the approximately poloidal/radial direction. To convert to
these coordinates, run

`PyMess.MAG.SaveAllRotatedData()`

#### To read converted data:

For MSO data:

`data = PyMess.MAG.ReadMagData(Date)`

For rotated data:

`data = PyMess.MAG.ReadRotatedData(Date)`

Also, for magnetopause normal data (based on the magnetopause used by
the KT17 magnetic field model):

`data = PyMess.MAG.MagDataMPN(Date)`

#### To plot data:

`PyMess.MAG.PlotMagData(Date,ut=ut,MagType=MagType)`

Where, `Date` is a one or two element integer, with the format yyyymmdd,
ut is a two element list, array or tuple, denoting the time range 
(from 0 - 24)  and MagType is a string equal to one of the following:
`'MSM'|'Rotated'|'MPN'`.

All of the aforementioned routines have a range of keywords which can be
found in their  docstrings.

### 3. `NS` - Neutron Spectrometer

This submodule contains some basic routines to convert the NS PDS data 
to a better binary format, and also to read the new data.

#### Convert PDS data:

Place PDS files in `$MESSENGER_PATH/NS/PDS`, where the code will look
for them, then run:

`PyMess.NS.PDS.ConvertToBinary()`

#### Read converted data:

