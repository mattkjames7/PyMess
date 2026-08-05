"""Plot combined MESSENGER FIPS spectra as a time-energy grid."""

import matplotlib.pyplot as plt
from matplotlib.colors import LogNorm,Normalize
import numpy as np
import DateTimeTools as TT

from .GetData import GetData
from .PlotFIPS import _Axes


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


def _WithGaps(time,coordinate,spectra,MaxGap):
	"""Insert empty columns so pcolormesh does not bridge data gaps."""
	if MaxGap is None or time.size < 2:
		return time,coordinate,spectra
	gaps = np.where(np.diff(time) > MaxGap/3600.0)[0]
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


def PlotFIPSSpectrogram(Date,ut,Param='Flux',Y='Energy',fig=None,
						maps=(1,1,0,0),ylog=True,zlog=True,no_x=False,
						MaxGap=120.0,Type='60H',cmap='gnuplot',Colorbar=True,
						vmin=None,vmax=None,**kwargs):
	"""Plot a time series of combined FIPS spectra as a two-dimensional grid.

	Parameters
	----------
	Date, ut
		Date and UT selection accepted by :func:`PyMess.FIPS.GetData`.
	Param : str
		Spectral variable: ``Counts``, ``Flux``, ``PSD`` or ``Efficiency``.
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
		Combined-data type, such as ``60H``, ``60He`` or ``10H``.
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
	parameter = _SpectrumAliases.get(str(Param).lower())
	if parameter is None:
		raise ValueError(
			'Unknown spectral parameter {!r}; choose from {}'.format(
				Param,', '.join(Spectra)
			)
		)
	coordinate_name = _CoordinateAliases.get(str(Y).lower())
	if coordinate_name is None:
		raise ValueError('Unknown vertical coordinate {!r}; choose Energy or Velocity'.format(Y))

	data = GetData(Date,ut=ut,Type=Type,Verbose=False)
	if data.size == 0:
		raise ValueError('No {:s} FIPS data found in the requested interval'.format(Type))

	color_label,field = Spectra[parameter]
	ylabel,coordinate_field = Coordinates[coordinate_name]
	time = np.asarray(data.utc,dtype='float64')
	coordinate = np.asarray(data[coordinate_field],dtype='float64')
	values = np.asarray(data[field],dtype='float64')
	order = np.argsort(time)
	time = time[order]
	coordinate = coordinate[order]
	values = values[order]
	time,coordinate,values = _WithGaps(time,coordinate,values,MaxGap)

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
	else:
		TT.DTPlotLabel(ax,Seconds=False,IncludeYear=False)
		ax.set_xlabel('UT')

	if Colorbar:
		colorbar = ax.figure.colorbar(mesh,ax=ax,pad=0.02)
		colorbar.set_label(color_label)
	return ax
