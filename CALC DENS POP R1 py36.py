'''
Created on: see version log.
@author: rigonz
coding: utf-8

IMPORTANT: requires py3.6 (rasterio)

Script that:
1) reads a series of raster files,
2) computes aggregated statistics,
3) makes charts showing the results.

The input data files correspond to countries and represent population.
For each country there is one file with the count of people per cell/pixel.

The script calculates the projected area of each cell and from it the density.

The script loops over the cells to prepare charts that present the distribution
of the population according to the density.

The calculations are run over each country.

The charts present the results for each country and for the group of countries.
Chars are in relative (% in 0-1 range) and absolute (total population) terms.

The raster data is prepared separately, in specific GIS software.

Version log.
R0 (20210506):
First trials.

R1 (20210507):
Creates a new geotiff with the densities and saves it.
Does not create plots.

'''

# %% Imports.
from pyproj import Geod
import rasterio  # IMPORTANT: requires py3.6
import numpy as np

# %% Directories.
RootDirIn = 'D:/0 DOWN/zz EXTSave/GIS/POP/EUR/SHP/WP/'

# Country codes.
l_ctry = ['FRA', 'ITA', 'DEU', 'ESP']
l_ctry = ['ITA', 'DEU', 'ESP']
#l_ctry = ['FRA']

# %% Read and compute.
# Auxiliaries:
geod = Geod('+a=6378137 +f=0.0033528106647475126')

# Main loop:
for ctry in l_ctry:

    # Update the user with the progress:
    print('\nStarting {}.'.format(ctry))

    # Open file and read data:
    print('Opening and reading the data files...')
    FileNameI = RootDirIn + ctry + '_ppp_2020_UNadj_constrained.tif'
    dataset = rasterio.open(FileNameI)
    band_c = dataset.read(1)
    
    # Check CRS:
    try:
        if dataset.crs.data['init'] != 'epsg:4326':
            print('WARNING: CRS is not EPSG4326 for {}.'.format(ctry))
    except:
        print('WARNING: CRS is not available for {}.'.format(ctry))
    
    # Calculate areas:
    print('Calculating the densities...')
    dlon = dataset.transform[0]  # increase in lon between adjacent cells; dataset.res[0]
    dlat = dataset.transform[4]  # increase in lat between adjacent cells; dataset.res[1]
    lon0 = dataset.transform[2]  # lon of upper left cell
    lat0 = dataset.transform[5]  # lat of upper left cell

    band_d = np.full_like(band_c, -99999)
    count = int(dataset.shape[0]/20)
    for i in range(0, dataset.shape[0] - 1, 1):
        for j in range(0, dataset.shape[1] - 1, 1):
            if band_c[i, j] > 0:
                lons = [lon0 + dlon*j, lon0 + dlon*j, lon0 + dlon*(j+1), lon0 + dlon*(j+1)]
                lats = [lat0 + dlat*i, lat0 + dlat*(i+1), lat0 + dlat*(i+1), lat0 + dlat*i]
                area, perim = geod.polygon_area_perimeter(lons, lats)
                band_d[i, j] = band_c[i, j] / area * 1E6  # area in m2, d in hab/km2

        # Update the user with the progress:
        if i % count == 0:
            print('PopDens_{}: {:4.1f}%'.format(ctry, i/dataset.shape[0]*100))


    # Save the results:
    print('Saving the results...')
    FileNameO = FileNameI.replace('.tif', '_d.tif')
    with rasterio.open(FileNameO,'w', driver='GTiff',
                       height=band_d.shape[0], width=band_d.shape[1], count=1,
                       dtype=band_d.dtype, crs=dataset.crs,
                       transform=dataset.transform, compress='lzw') as dataset_d:
        dataset_d.write(band_d, 1)

# %% Script done.
print('\nScript completed. Thanks!')
