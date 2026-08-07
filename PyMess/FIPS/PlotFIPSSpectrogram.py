"""Plot combined MESSENGER FIPS spectra as a time-energy grid."""

import matplotlib.pyplot as plt
from matplotlib.colors import LogNorm,Normalize
import numpy as np
import DateTimeTools as TT

from .GetData import GetData
from .PlotFIPS import _Axes
from .. import Globals


Spectra = {
	'Counts': ('Counts', 'Counts'),
	'Flux': (
		'Differential energy flux ((keV/e)$^{-1}$ s$^{-1}$ cm$^{-2}$ sr$^{-1}$)',
		'Flux',
	),
	'PSD': ('Phase-space density (s$^3$ m$^{-6}$)', 'PSD'),
	'Efficiency': ('Detection efficiency', 'Efficiency'),
}

_SpectrumAliases = {name.lower(): name for name in Spectra}

_FluxLabel = 'Differential energy flux ((keV/e)$^{-1}$ s$^{-1}$ cm$^{-2}$ sr$^{-1}$)'

Coordinates = {
	'Energy': ('Energy/charge (keV/e)', 'EQBins'),
	'Velocity': ('Velocity (km s$^{-1}$)', 'VBins'),
}

_CoordinateAliases = {
	'energy': 'Energy',
	'e': 'Energy',
	'e/q': 'Energy',
	'eq': 'Energy',
	'eqbins': 'Energy',
	'velocity': 'Velocity',
	'v': 'Velocity',
	'vbins': 'Velocity',
}


def _WithGaps(time,coordinate,spectra,MaxGap,SecondsPerUnit=3600.0):
	"""Insert empty columns so pcolormesh does not bridge data gaps."""
	if MaxGap is None or time.size < 2:
		return time,coordinate,spectra
	gaps = np.where(np.diff(time) > MaxGap/SecondsPerUnit)[0]
	if gaps.size == 0:
		return time,coordinate,spectra

	new_size = time.size + gaps.size
	new_time = np.empty(new_size,dtype='float64')
	new_coordinate = np.empty((new_size,coordinate.shape[1]),dtype='float64')
	new_spectra = np.full((new_size,spectra.shape[1]),np.nan,dtype='float64')
	gap_set = set(gaps.tolist())
	out = 0
	for i in range(time.size):
		new_time[out] = time[i]
		new_coordinate[out] = coordinate[i]
		new_spectra[out] = spectra[i]
		out += 1
		if i in gap_set:
			new_time[out] = 0.5*(time[i] + time[i + 1])
			new_coordinate[out] = 0.5*(coordinate[i] + coordinate[i + 1])
			out += 1
	return new_time,new_coordinate,new_spectra


def _Norm(values,zlog,vmin,vmax):
	finite = values[np.isfinite(values)]
	if zlog:
		finite = finite[finite > 0]
	if finite.size == 0:
		raise ValueError('The requested spectrum contains no plottable values')
	if vmin is None:
		vmin = np.nanmin(finite)
	if vmax is None:
		vmax = np.nanmax(finite)
	if vmax <= vmin:
		# Matplotlib requires a nonzero normalization range.
		vmax = vmin*(1.0 + 1.0e-6) if vmin != 0 else 1.0
	return LogNorm(vmin=vmin,vmax=vmax) if zlog else Normalize(vmin=vmin,vmax=vmax)


def _Spectrum(Type,Param,fields):
	"""Resolve user-facing parameters onto each PDS/combined product."""
	product = str(Type).lower()
	requested = '' if Param is None else str(Param).lower()
	if product == 'edr':
		if requested not in ('','counts','rate','protonrate','proton_rate'):
			raise ValueError('EDR supports Param="ProtonRate" (or "Counts")')
		return 'Proton rate','ProtonRate','H'
	if product == 'cdr':
		if requested not in ('','flux','protonflux','proton_flux'):
			raise ValueError('CDR supports Param="ProtonFlux" (or "Flux")')
		return _FluxLabel,'ProtonFlux','H'
	if product == 'espec':
		aliases = {
			'':'H','flux':'H','h':'H','hflux':'H',
			'he2':'He2','he2flux':'He2','he++':'He2',
			'he':'He','heflux':'He',
			'na':'Na','naflux':'Na','na_group':'Na',
			'o':'O','oflux':'O','o_group':'O',
		}
		ion = aliases.get(requested)
		if ion is None:
			raise ValueError(
				'ESPEC Param must be H, He2, He, Na or O (optionally suffixed Flux)'
			)
		return '{} {}'.format(ion,_FluxLabel),'{}Flux'.format(ion),ion

	parameter = 'Flux' if Param is None else _SpectrumAliases.get(requested)
	if parameter is None:
		raise ValueError(
			'Unknown spectral parameter {!r}; choose from {}'.format(
				Param,', '.join(Spectra)
			)
		)
	label,field = Spectra[parameter]
	if field not in fields:
		raise ValueError('{:s} data do not contain the {:s} spectrum'.format(Type,field))
	return label,field,'H'


def _MatchScanType(Date,ut,data):
	"""Match ESPEC records to the nearest EDR scan using mission time."""
	edr = GetData(Date,ut=ut,Type='edr',Verbose=False)
	if edr.size == 0:
		raise ValueError('Cannot reconstruct ESPEC bins because no matching EDR data exist')
	edr_met = np.asarray(edr.MET,dtype='float64')
	order = np.argsort(edr_met)
	edr_met = edr_met[order]
	scan_type = np.asarray(edr.ScanType)[order]
	met = np.asarray(data.MET,dtype='float64')
	position = np.searchsorted(edr_met,met)
	position = np.clip(position,0,edr_met.size - 1)
	previous = np.maximum(position - 1,0)
	use_previous = (
		np.abs(edr_met[previous] - met) <= np.abs(edr_met[position] - met)
	)
	position[use_previous] = previous[use_previous]
	return scan_type[position]


def _Coordinate(Date,ut,Type,data,coordinate_name,ion):
	"""Load stored bins or reconstruct them from the appropriate scan table."""
	field = Coordinates[coordinate_name][1]
	fields = data.dtype.names or ()
	if field in fields:
		return np.asarray(data[field],dtype='float64')
	if 'ScanType' in fields:
		scan_type = np.asarray(data.ScanType)
	elif str(Type).lower() == 'espec':
		scan_type = _MatchScanType(Date,ut,data)
	else:
		raise ValueError('Cannot reconstruct spectral bins without ScanType')

	energy = np.vstack([
		Globals.EQBins.get(int(value),Globals.EQBins[0]) for value in scan_type
	]).astype('float64')
	if coordinate_name == 'Energy':
		return energy
	mass = Globals.Constants.amu*Globals.IonMass[ion]
	charge = 2.0 if ion == 'He2' else 1.0
	return np.sqrt(charge*Globals.Constants.e*2000.0*energy/mass)/1000.0


def PlotFIPSSpectrogram(Date,ut,Param=None,Y='Energy',fig=None,
						maps=(1,1,0,0),ylog=True,zlog=True,no_x=False,
						MaxGap=120.0,Type='60H',cmap='gnuplot',Colorbar=True,
						vmin=None,vmax=None,**kwargs):
	"""Plot a time series of combined FIPS spectra as a two-dimensional grid.

	Parameters
	----------
	Date, ut
		Date and UT selection accepted by :func:`PyMess.FIPS.GetData`.
	Param : str, optional
		Spectrum to plot. Defaults to proton rate for EDR, proton flux for
		CDR, H flux for ESPEC, and flux for combined data. ESPEC also accepts
		``He2``, ``He``, ``Na`` and ``O``.
	Y : str
		Vertical coordinate: ``Energy`` (energy/charge) or ``Velocity``.
	fig, maps
		Plot target and legacy subplot location used by :func:`PlotFIPS`.
	ylog, zlog : bool
		Use logarithmic vertical and colour scales respectively.
	no_x : bool
		Hide the time-axis label and tick labels.
	MaxGap : float or None
		Insert empty columns across gaps larger than this many seconds.
	Type : str
		Data product, including ``edr``, ``cdr``, ``espec`` and combined
		types such as ``60H``, ``60He`` or ``10H``.
	cmap : str or Colormap
		Matplotlib colour map; defaults to ``gnuplot``.
	Colorbar : bool
		Add a labelled colour bar when true.
	vmin, vmax : float, optional
		Colour normalization bounds.
	**kwargs
		Additional arguments passed to ``Axes.pcolormesh``.

	Returns
	-------
	matplotlib.axes.Axes
	"""
	coordinate_name = _CoordinateAliases.get(str(Y).lower())
	if coordinate_name is None:
		raise ValueError('Unknown vertical coordinate {!r}; choose Energy or Velocity'.format(Y))

	data = GetData(Date,ut=ut,Type=Type,Verbose=False)
	if data.size == 0:
		raise ValueError('No {:s} FIPS data found in the requested interval'.format(Type))

	fields = data.dtype.names or ()
	color_label,field,ion = _Spectrum(Type,Param,fields)
	ylabel,coordinate_field = Coordinates[coordinate_name]
	if 'unix' in fields:
		time = np.asarray(data.unix,dtype='float64')
		time_format = 'unix'
		seconds_per_unit = 1.0
	elif 'MET' in fields:
		time = np.asarray(data.MET,dtype='float64')
		time_format = 'met'
		seconds_per_unit = 1.0
	else:
		raise ValueError('FIPS data contain neither a unix nor MET time field')
	coordinate = _Coordinate(Date,ut,Type,data,coordinate_name,ion)
	values = np.asarray(data[field],dtype='float64')
	order = np.argsort(time)
	time = time[order]
	coordinate = coordinate[order]
	values = values[order]
	time,coordinate,values = _WithGaps(
		time,coordinate,values,MaxGap,SecondsPerUnit=seconds_per_unit
	)

	# FIPS bins are stored from high to low energy; pcolormesh is clearer
	# with the vertical coordinate ordered from low to high.
	coordinate = coordinate[:,::-1]
	values = values[:,::-1]
	xgrid = np.broadcast_to(time,(coordinate.shape[1],time.size))
	ygrid = coordinate.T
	zgrid = values.T

	norm = _Norm(zgrid,zlog,vmin,vmax)
	if zlog:
		zgrid = np.ma.masked_less_equal(zgrid,0.0)
	else:
		zgrid = np.ma.masked_invalid(zgrid)

	ax = _Axes(fig,maps)
	kwargs.setdefault('shading','nearest')
	kwargs.setdefault('rasterized',True)
	mesh = ax.pcolormesh(xgrid,ygrid,zgrid,cmap=cmap,norm=norm,**kwargs)
	ax.set_ylabel(ylabel)
	if ylog:
		ax.set_yscale('log')

	if no_x:
		ax.tick_params(axis='x',which='both',bottom=False,labelbottom=False)
		ax.set_xlabel('')
	elif time_format == 'unix':
		TT.DTPlotLabel(ax,Seconds=False,IncludeYear=False,TimeFMT='unix')
		ax.set_xlabel('UT')
	else:
		ax.set_xlabel('MET (s)')

	if Colorbar:
		colorbar = ax.figure.colorbar(mesh,ax=ax,pad=0.02)
		colorbar.set_label(color_label)
	return ax
