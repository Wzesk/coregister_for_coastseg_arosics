# coregister_for_coastseg_arosics

This is a set of scripts that uses the arosics package to allow users to perform global coregistration on folders on tiffs. This colleciton of scripts includes some that are designed to work specifically with CoastSeg sessions. 

## Compatible Satellites
1. PlanetScope
2. Landsat 5,8,9
3. S2

# Install Instructions
```
conda create -n coreg python=3.11 -y
conda activate coreg
conda install -c conda-forge arosics gdal coastsat_package rasterio
```

# Credits
Thanks to [arosics](https://github.com/GFZ/arosics) for making this possible.
