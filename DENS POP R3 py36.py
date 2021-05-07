'''
Created on: see version log.
@author: rigonz
coding: utf-8

IMPORTANT: requires py3.6 (rasterio)

Script that:
1) reads a series of raster files,
2) computes aggregated statistics,
3) makes charts showing the results..

The input data files correspond to countries and represent population.
For each country there are two files:
- _c, with the count of people per cell,
- _d, with the density of people per cell.

The script loops over the cells to prepare charts that present the distribution.
of the population according to the density.

The calculations are run over each country.
The charts present the comparison for the group of countries.

The raster data is prepared separately, in specific GIS software.
The source of the data is CIESIN, GPW v4.

Version log (ipynb).
R1 (20200913):
First trials.

Version log (py).
R1 (20210506):
Converted from ipybn to py.
Updates names.
Adds checks to verify that both datasets are comparable.
Simplifies the calculations by reducing the dimensions.

R2 (20210507):
Usdes masks instead of list comprehensions, much quicker.

'''

# %% Imports.
import rasterio  # IMPORTANT: requires py3.6
import numpy as np
from matplotlib import pyplot as plt

# %% Directories.
RootDirIn = 'D:/0 DOWN/zz EXTSave/GIS/POP/EUR/SHP/WP/'

# Country codes.
l_ctry = ['FRA', 'ITA', 'DEU', 'ESP']
#l_ctry = ['FRA']

# %% Read and compute.
# Auxiliaries:
bin_int = 100  # bin increment, hab/km2, for the population density.
l_all = []

# Main loop:
for ctry in l_ctry:

    # Update the user of the progress:
    print('\nStarting {}.'.format(ctry))

    # Filenames:
    FileNameI1 = RootDirIn + ctry + '_ppp_2020_UNadj_constrained.tif'
    FileNameI2 = RootDirIn + ctry + '_ppp_2020_UNadj_constrained_d.tif'

    # Open files:
    print('Opening and reading the files...')
    dataset_c = rasterio.open(FileNameI1)
    dataset_d = rasterio.open(FileNameI2)

    # Verify that the datasets are comparable.
    # Bounds:
    if dataset_c.bounds != dataset_d.bounds:
        print('WARNING: bounds are not the same for {:s}.'.format(ctry))
    # Width and height:
    if dataset_c.width != dataset_d.width:
        print('WARNING: widths are not the same for {:s}.'.format(ctry))
    if dataset_c.height != dataset_d.height:
        print('WARNING: heighths are not the same for {:s}.'.format(ctry))
    # Bands:
    if dataset_c.indexes[0] != dataset_d.indexes[0]:
        print('WARNING: bands are not the same for {:s}.'.format(ctry))

    # Read data:
    band_c = dataset_c.read(1)
    band_d = dataset_d.read(1)

    # Verify that the dimensions are the same:
    if band_c.shape != band_d.shape:
        print('WARNING: shapes are not the same for {:s}.'.format(ctry))

    # Flatten:
    print('Preparation of data...')
    band_c = band_c.flatten()
    band_d = band_d.flatten()

    # Create and apply mask:
    band_mask = np.array(np.minimum(band_c, band_d) <= 0)  # c and d <= 0   
    band_c = np.delete(band_c, band_mask)
    band_d = np.delete(band_d, band_mask)

    # Make bins:
    bin_d = range(-bin_int, int(np.ceil(band_d.max() / bin_int) + 1) * bin_int, bin_int)

    # Compute:
    print('Calculating the distribution...')
    l_res = []
    count = 0
    for bin_val in bin_d:
        l_res.append([bin_val, np.where(band_d < bin_val, band_c, 0).sum()])

        # Update the user of the progress:
        if count % int(len(bin_d)/20) == 0:
            print('{} {:4.1f}%'.format(ctry, count/len(bin_d)*100))
        count += 1

    # Save results:
    l_x = [x[0] for x in l_res]
    l_y = [x[1] for x in l_res]
    l_all.append([ctry, l_x, l_y])

# %% Draw charts: absolute and relative population, separate charts.
# Auxiliaries:
color = ['k', 'r', 'b', 'g']

# Main loop:
for ctry_i in range(0, len(l_ctry), 1):

    # Absolute population:
    l_x = [x for x in l_all[ctry_i][1]]
    l_y = [x for x in l_all[ctry_i][2]]
    plt.scatter(l_x, l_y, color=color[ctry_i], s=1.0)

    # Set the titles:
    plt.title(l_all[ctry_i][0], loc='right')
    plt.xlabel('dens., hab/km2')
    plt.ylabel('abs_cum_pop.')

    # Axis:
    plt.grid(True)

    # Tightlayout:
    plt.tight_layout()

    # Take a look:
    plt.show()

    # Relative population:
    pop_s = l_all[ctry_i][2][-1]
    l_x = [x for x in l_all[ctry_i][1]]
    l_y = [x / pop_s for x in l_all[ctry_i][2]]
    plt.scatter(l_x, l_y, color=color[ctry_i], s=1.0)

    # Set the titles:
    plt.title(l_all[ctry_i][0], loc='right')
    plt.xlabel('dens., hab/km2')
    plt.ylabel('rel_cum_pop.')

    # Axis:
    plt.grid(True)

    # Tightlayout:
    plt.tight_layout()

    # Take a look:
    plt.show()

# %% Draw charts: absolute and relative population, join charts.
# Auxiliaries:
color = ['k', 'r', 'b', 'g']

# Absolute population:
for ctry_i in range(0, len(l_ctry), 1):
    l_x = [x for x in l_all[ctry_i][1]]
    l_y = [x for x in l_all[ctry_i][2]]
    plt.plot(l_x, l_y, color=color[ctry_i], label=l_all[ctry_i][0])

# Others:
plt.xlabel('dens., hab/km2')
plt.ylabel('cum_pop.')
plt.legend()
plt.grid(True)
plt.tight_layout()
plt.xlim(0,40000)
plt.show()

# Relative population:
for ctry_i in range(0, len(l_ctry), 1):
    pop_s = l_all[ctry_i][2][-1]
    l_x = [x for x in l_all[ctry_i][1]]
    l_y = [x / pop_s for x in l_all[ctry_i][2]]
    plt.plot(l_x, l_y, color=color[ctry_i], label=l_all[ctry_i][0])

# Others:
plt.xlabel('dens., hab/km2')
plt.ylabel('rel_cum_pop')
plt.legend()
plt.grid(True)
plt.tight_layout()
plt.xlim(0,60000)
plt.ylim(0.6, 1.0)
plt.show()

# %% Draw charts: absolute and relative population, join charts.
# Auxiliaries:
color = ['k', 'r', 'b', 'g']

# Relative population:
for ctry_i in range(0, len(l_ctry), 1):
    pop_s = l_all[ctry_i][2][-1]
    l_x = [x for x in l_all[ctry_i][1]]
    l_y = [x / pop_s for x in l_all[ctry_i][2]]
    plt.plot(l_x, l_y, color=color[ctry_i], label=l_all[ctry_i][0])

# Others:
plt.xlabel('dens., hab/km2')
plt.ylabel('rel_cum_pop')
plt.xlim(0,60000)
plt.ylim(0.6, 1.0)

plt.legend()
plt.grid(True)
plt.tight_layout()
plt.show()

# %% Script done.
print('\nScript completed. Thanks!')
