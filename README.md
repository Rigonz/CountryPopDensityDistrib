# CountryPopDensityDistrib
The distribution of the population density within a country.

## Presentation
This repository aims at answering the following related questions:

* There are sparsely populated wide areas, and densely populated neighborhoods, but how much people live on each of them? 
* In brief: what is the distribution of the population density for a given country? 
* And, can we get that for any country?

## Data
The script reads geotiff raster files. For each country a raster with population counts and another with population densities are required.
I have used the Gridded Population of the World ([GPW v4](https://sedac.ciesin.columbia.edu/data/collection/gpw-v4/sets/browse)), as it provides reliable data, world coverage, fairly good granularity (up to 30 arc-seconds) and several years (2000, 2005, 2010, 2020). 

Other providers of similar datasets exist, for instance:
* [WorldPop](https://www.worldpop.org/project/categories?id=3)
* [GHSL](https://ghsl.jrc.ec.europa.eu/datasets.php)
* [LandScan](https://landscan.ornl.gov/)

But while this information is also of high quality, it refers to counts per cell, not densities. It is possible to compute the density, but as I preferred that the script remained as simple as possible, I have sticked to GPW.

The input datafiles need to be clipped to the desired boundary. Clipping can also be scripted, but it is not done here. (I use QGIS).

I use the term "country" but any border desired by the user at the time of clipping will do.

## Output
The script generates several charts:
* For each country: the distribution of population density, on absolute (total population) and relative (%) terms.
* For the set of specified countries: combined plots on absolute and relative terms. 

![Combined_1](https://github.com/Rigonz/CountryPopDensityDistrib/Images/Figure All_A 01.png)

## Running the script
The script uses the library [rasterio](https://rasterio.readthedocs.io/en/latest/index.html#), which I have not been able to run under python 3.8: it works well under 3.6.

The script is uploaded as working on my computer: modifying the location of the files and other preferences is quite straightforward.
