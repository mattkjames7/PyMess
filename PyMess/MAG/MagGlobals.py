import numpy as np
from .. import Globals

paths = {	'Dip': Globals.MessPath + '/MAG/Binary/Rotated/',
			'MSM': Globals.MessPath+'MAG/Binary/MSO/',
			'MSO': Globals.MessPath+'MAG/Binary/MSO/',
			'MPN': Globals.MessPath+'MAG/Binary/MPN/'}
			

			


msmdtype = [('Date','int32'),
			('ut','float32'),
			('utc','float64'),
			('Xmso','float32'),
			('Ymso','float32'),
			('Zmso','float32'),
			('Xmsm','float32'),
			('Ymsm','float32'),
			('Zmsm','float32'),
			('Bx','float32'),
			('By','float32'),
			('Bz','float32')]	
			
mpndtype = [('Date','float32'),
			('ut','float32'),
			('utc','float64'),
			('BN','float32'),
			('BM','float32'),
			('BL','float32'),
			('pN','float32'),
			('pM','float32'),
			('pL','float32'),
			('xMP','float32'),
			('yMP','float32'),
			('zMP','float32'),
			('nx','float32'),
			('ny','float32'),
			('nz','float32'),
			('E','float32'),
			('r','float32'),
			('phi','float32'),
			('Xmsm','float32'),
			('Ymsm','float32'),
			('Zmsm','float32')]


dipdtype=[	('Date','int32'),
			('ut','float32'),
			('utc','float64'),
			('Bpol','float32'),
			('Btor','float32'),
			('Bpar','float32'),
			('Xmsm','float32'),
			('Ymsm','float32'),
			('Zmsm','float32')]


dtypes = {	'Dip': dipdtype,
			'MSM': msmdtype,
			'MSO': msmdtype,
			'MPN': mpndtype}
