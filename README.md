# CountryPopDensityDistrib
The distribution of the population density within a country.

## Presentation
This repository aims at answering the following related questions:

* There are sparsely populated areas and densely populated neighborhoods, but how much people live on each of them? 
* In brief: what is the distribution of the population density for a given country? 
* And, can we get that for any country in the world?

I employ in this readme the term "country", but any boundary desired by the user will do.

## Data
The script [DENS POP](https://github.com/Rigonz/CountryPopDensityDistrib/blob/main/DENS%20POP%20R2%20py36.py) reads geotiff raster files. For each country a raster with population counts and another with population densities are required.

I have used the Gridded Population of the World ([GPW v4](https://sedac.ciesin.columbia.edu/data/collection/gpw-v4/sets/browse)), as it provides reliable data, world coverage, fairly good granularity (up to 30 arc-seconds) and several years (2000, 2005, 2010, 2020). 

Other providers of similar datasets exist, for instance:
* [WorldPop](https://www.worldpop.org/project/categories?id=3)
* [GHSL](https://ghsl.jrc.ec.europa.eu/datasets.php)
* [LandScan](https://landscan.ornl.gov/)

While this information is also of high quality, it refers to counts per cell, not densities. The script [CALC DENS POP](https://github.com/Rigonz/CountryPopDensityDistrib/blob/main/CALC%20DENS%20POP%20R1%20py36.py) computes the population density from a raster with population counts, so it can be used to generate the density rasters required by "DENS POP".

The input datafiles need to be clipped to the desired boundary. Clipping can also be scripted, but it is not done here (I use QGIS).

## Output
The script generates several charts:
* For each country: the distribution of population density, on absolute (total population) and relative (%, on 0-1 scale) terms.
* For the set of specified countries: combined plots on absolute and relative terms. 

![Combined_1](https://github.com/Rigonz/CountryPopDensityDistrib/blob/main/Images/All_A_01.png)
![Combined_2](https://github.com/Rigonz/CountryPopDensityDistrib/blob/main/Images/All_R_02.png)
![ESP_1](https://github.com/Rigonz/CountryPopDensityDistrib/blob/main/Images/ESP_R.png)

## Running the scripts
The scripts are written in Python. They both use the library [rasterio](https://rasterio.readthedocs.io/en/latest/index.html#), which I have not been able to run under python 3.8, but it works well under python 3.6.

Both scripts are uploaded as they are on my computer: modifying the location of the files and other preferences should be quite straightforward.

