# Print the authors' published global RMSE (benchmark_results, 240x121, 2020) at the target leads
import sys
from scipy.io import netcdf_file
for path in sys.argv[1:]:
	f = netcdf_file(path, 'r', mmap=False)
	v = f.variables
	regions = [b''.join(r).decode() for r in v['region'].data]
	leads = list(v['lead_time'].data)
	levels = list(v['level'].data)
	g = regions.index('global')
	print(path.split('/')[-1], 'dims', v['rmse.geopotential'].dimensions)
	for var, lev in (('geopotential', 500), ('temperature', 850)):
		row = []
		for h in (24, 72, 120, 168, 240):
			row.append('%.4f' % v['rmse.' + var].data[g, leads.index(h), levels.index(lev)])
		print('  %s%d 1/3/5/7/10 d: %s' % (var, lev, ' '.join(row)))
