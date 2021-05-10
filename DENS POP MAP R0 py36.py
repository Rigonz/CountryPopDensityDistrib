'''
Created on: see version log.
@author: rigonz
coding: utf-8

IMPORTANT: requires py3.6 (rasterio)

Script that:
1) reads a series of raster files,
2) computes aggregated statistics,
3) creates a new raster showing the results.

The input data file corresponds to a country and represent population.
There are two raster input files:
- one with the count of people per cell/pixel (ppp),
- another with the population density (hab/km2).

The script:
- loops over the cells of the input rasters,
- defines an area around the selected cell,
- calculates the distribution of population density in that area,
- assigns the median of the population density to the pixel in the center,
- creates a new raster with the calculated medians.

Follows "CALC DENS POP R1 py36.py" for the calculation of the distribution of
population density.

Version log.
R0 (20210509):
First trials.

'''

# %% Imports.
import rasterio  # IMPORTANT: requires py3.6
from rasterio.transform import Affine
from pyproj import Geod
import numpy as np

# %% Directories.
RootDirIn = 'D:/0 DOWN/zz EXTSave/GIS/POP/EUR/SHP/WP/'

ctry = 'ESP'
FileNameI1 = RootDirIn + ctry + '_ppp_2020_UNadj_constrained.tif'
FileNameI2 = RootDirIn + ctry + '_ppp_2020_UNadj_constrained_d.tif'

# %% Open file and read data.
print('Opening and reading the data files...')
dataset_c = rasterio.open(FileNameI1)
dataset_d = rasterio.open(FileNameI2)
band_c = dataset_c.read(1)
band_d = dataset_d.read(1)

# %% Input checks:
print('Checking the input data...')
# CRS:
try:
    if (dataset_c.crs.data['init'] != 'epsg:4326' or
        dataset_d.crs.data['init'] != 'epsg:4326'):
        print('WARNING: CRS is not EPSG4326.')
except:
    print('WARNING: CRS is not available or is not the same in both files.')

# Boundaries:
if (dataset_c.transform[4] != dataset_d.transform[4] or
    dataset_c.transform[2] != dataset_d.transform[2]):
    print('WARNING: bounds are not the same in both files.')

# Boundaries:
if (dataset_c.transform[2] != dataset_d.transform[2] or
    dataset_c.transform[5] != dataset_d.transform[5]):
    print('WARNING: resolutions are not the same in both files.')

# %% Input auxiliaries.
geod = Geod('+a=6378137 +f=0.0033528106647475126')  # for WGS84.
dlon = dataset_c.transform[0]  # delta_lon btw adjacent cells; dataset.res[0]
dlat = dataset_c.transform[4]  # delta_lat btw adjacent cells; dataset.res[1]
lon0 = dataset_c.transform[2]  # lon of upper left cell
lat0 = dataset_c.transform[5]  # lat of upper left cell

# %% Output auxiliaries.
res_m = 10  # New resolution multiple (if res_m=1 -> same resolution as input.
band_o = np.full((band_c.shape[0]//res_m, band_c.shape[1]//res_m), -99999)

# Half-side of the square that defines the area for calculation of the
# distribution of the population density.
dst = 5000  # m

# Number of pixels that define the squared area around the pixel of interest:
nx = int(np.ceil(abs(dst/geod.a/dlon*180/np.pi)))
ny = int(np.ceil(abs(dst/geod.a/dlat*180/np.pi)))

# Make bins:
bin_int = 50  # bin increment, hab/km2, for the population density.
bin_d = range(-bin_int,
              int(np.ceil(band_d.max() / bin_int) + 1) * bin_int, bin_int)

# %% Main loop.
print('Computing the results...')

count = 0
for i_o in range(0, band_o.shape[0], 1):
    i_i = (band_c.shape[0] % res_m) // 2 + i_o * res_m
    for j_o in range(0, band_o.shape[1], 1):
        j_i = (band_c.shape[1] % res_m) // 2 + j_o * res_m

        # The block's center is [i_i, j_i] and has ni/nj rows/cols around it:
        slc_i = slice(max(0, i_i - ny), min(band_c.shape[0], i_i + ny + 1), 1)
        slc_j = slice(max(0, j_i - nx), min(band_c.shape[1], j_i + nx + 1), 1)

        # The difference btw consecutive blocks is the extreme columns.
        # This could be used to simplify the array operations:
        # if slice_i.start > 0 and slice_i.stop < band_c.shape[1]:
        # etc
        # else:
        # etc

        band_c1 = band_c[slc_i, slc_j]
        band_d1 = band_d[slc_i, slc_j]

        # Flatten and apply mask:
        band_c1 = band_c1.flatten()
        band_d1 = band_d1.flatten()
        band_ma = np.array(np.minimum(band_c1, band_d1) <= 0)
        band_c1 = np.delete(band_c1, band_ma)
        band_d1 = np.delete(band_d1, band_ma)

        # Compute the median:
        pop_ref = band_c1.sum() * 0.5
        pop_cum = 0
        k = 0
        while pop_cum < pop_ref and k < len(bin_d):
            pop_cum = np.where(band_d1 < bin_d[k], band_c1, 0).sum()
            k += 1

        # Save results:
        if k >= len(bin_d):
            band_o[i_o, j_o] = 0
        else:
            band_o[i_o, j_o] = bin_d[k]

    # Show the progress:
    if count % int(band_o.shape[0]/100) == 0:
        print('Progress... {:4.1f}%'.format(count/band_o.shape[0]*100))
    count += 1

# %% Save the results.
print('Saving the results...')
# Coords of the upper-left pixel:
iUL = (band_c.shape[0] % res_m) // 2
jUL = (band_c.shape[1] % res_m) // 2
cUL = dataset_c.transform * (jUL, iUL)
# Affine transformations:
transform = Affine.translation(cUL[0], cUL[1]) * Affine.scale(res_m*dlon, res_m*dlat)
FileNameO = FileNameI1.replace('.tif', '_o.tif')
with rasterio.open(FileNameO,'w', driver='GTiff',
                   height=band_o.shape[0], width=band_o.shape[1], count=1,
                   dtype=band_o.dtype, crs=dataset_c.crs,
                   transform=transform, compress='lzw') as dataset_o:
    dataset_o.write(band_o, 1)

# %% Save the log10 results.
band_ol = np.log10(np.where(band_o <= 10, 10, band_o))
FileNameO = FileNameI1.replace('.tif', '_l.tif')
with rasterio.open(FileNameO,'w', driver='GTiff',
                   height=band_o.shape[0], width=band_o.shape[1], count=1,
                   dtype=band_ol.dtype, crs=dataset_c.crs,
                   transform=transform, compress='lzw') as dataset_o:
    dataset_o.write(band_ol, 1)

# %% Script done.
print('\nScript completed. Thanks!')
