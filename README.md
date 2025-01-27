# coregister_for_coastseg_arosics

This is a set of scripts that uses the arosics package to allow users to perform global coregistration on folders on tiffs. This colleciton of scripts includes some that are designed to work specifically with CoastSeg sessions. 

## Compatible Satellites
- PlanetScope
- Landsat 5, 8, 9
- Sentinel-2 (S2)

## Install Instructions
To set up your environment for using these scripts, follow these steps:
```bash
conda create -n coreg python=3.11 -y
conda activate coreg
conda install -c conda-forge arosics gdal coastsat-package rasterio
```

# Getting Started

<details>
<summary><strong>Example #1: Coregister a Single Image</strong></summary>

  In this example we will coregister a S2 scene to a Landsat 9 scene at Unalakleet Alaska.

1. Open the file `coregister_single.py`
2. Create the coregister settings
     - These are the settings that are provided to arosics to coregister the two scenes together.
     - You can read me more about the available settings at the  [arosics global coreg page](https://danschef.git-pages.gfz-potsdam.de/arosics/doc/arosics.html#module-arosics.CoReg)
     - I recommend using these default settings.
```
coregister_settings = {
    "ws": (256, 256), # window size: this is the size of the window used to calculate the coregistration shifts
    "nodata":(0,0),   # This is the no data value in the images
    "max_shift":100,  # This is the maximum allowable shift in pixels
    "binary_ws":False, # This forces the window size to be a power of 2
    "progress":False,  # This shows the progress of the coregistration
    "v":False,         # This shows the verbose output
    "ignore_errors":True, # Useful for batch processing. In case of error COREG.success == False and COREG.x_shift_px/COREG.y_shift_px is None        
    "fmt_out": "GTiff",
}
```
3. Enter the locations to the template and target images.
  - Replace the existing paths with the locations of your files
  - `im_reference` : This is the tiff file that you want to coregister the target to. 
  - `im_target` : This is the tiff file that you want to coregister to the template
  - Note: Neither of these files will be modified by the coregistration process. Any modifications will be saved to new directories and the finishes coregistered image will be saved out to the 'coregistered' directory
```
im_reference = "sample_data/2023-06-30-22-01-55_L9_ms.tif"
im_target = "sample_data/2023-10-09-22-28-02_S2_ms.tif" # This is the image that will be coregistered to the reference image
```
4. Run the script and the target image will be coregistered to the template image.
   - The coregistered image will be saved to 'coregistered' directory
   - A json file called `coreg_result.json` will be saved to the same directory. It contains the shift applied to the image
   - <bold> See content of  coreg_result.json </bold>
  ```
{
    "2023-10-09-22-28-02_S2_ms.tif": {
        "original_ssim": 0.5438432514482783,
        "coregistered_ssim": 0.5356732983691888,
        "change_ssim": -0.00816995307908952,
        "shift_x": -0.6070383489131927,
        "shift_y": 0.5041977167129517,
        "shift_x_meters": -6.0703834891319275,
        "shift_y_meters": -5.041977167129517,
        "shift_reliability": 73.24202217019764,
        "window_size": [
            256,
            256
        ],
        "success": true,
        "CRS": "EPSG:32604",
        "CRS_converted": true
    },
    "settings": {
        "ws": [
            256,
            256
        ],
        "nodata": [
            0,
            0
        ],
        "max_shift": 100,
        "binary_ws": false,
        "progress": false,
        "v": false,
        "ignore_errors": true,
        "fmt_out": "GTiff"
    }
}

  ```


</details>


# Credits
Thanks to [arosics](https://github.com/GFZ/arosics) for making this possible.
