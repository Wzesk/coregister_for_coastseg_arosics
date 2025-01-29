# CoastSeg Extentsion: Arosics for Coregistration 

This script collection utilizes the arosics package to enable global co-registration for directories containing TIFF files. Included are specialized scripts tailored for integration with CoastSeg sessions as well as additional scripts to co-register imagery.

This repository includes functions that can be used to:
1. Perform global coregistration with arosics
2. Filter out bad coregisteration results 
3. Apply coregisteration to coastseg sessions
    - Coregisters each satellite's tiff files within a CoastSeg session
    - Creates new jpgs based on the coregistered files
    - Saves all the coregistered files to a new directory

## Compatible Satellites
- PlanetScope
- Landsat 5, 8, 9
- Sentinel-2 (S2)

## Install Instructions
1. To set up your environment for using these scripts, follow these steps:
```bash
conda create -n coreg python=3.11 -y
conda activate coreg
conda install -c conda-forge arosics gdal coastsat-package rasterio
```

2. Activate your environment and git clone
```bash
conda activate coreg
git clone https://github.com/2320sharon/coregister_for_coastseg_arosics.git
cd coregister_for_coastseg_arosics
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

<details>
<summary><strong>Example #2 Coregister a CoastSeg Session</strong></summary>
  

Script : `coregister_coastseg_session.py`

This example takes a session folder from CoastSeg and coregisters all the tiff files for each of the satellites except L7 to the selected template. The tiff files in the `ms` directory for each satellite are used as the target images to coregister to the template image. After the shifts needed to coregister the images are calculated filtering is applied to remove any outliers. Any files that were flagged as outliers are moved to failed_coregistration folder in the output directory. For the files that passed the outlier filtering the estimated shifts are then applied to the panchromatic band, mask band, and QA band so that they match the coregistered ms band. Finally, it creates new jpg files based on the files that were coregistered.

### Directions
1. Open the file `coregister_single_planet_example.py`
2a. Create the coregister settings
These are the settings that are provided to arosics to coregister the two scenes together.
You can read me more about the available settings at the arosics global coreg page
I recommend using these default settings.
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
2b. Create the filter settings
These are the settings that are used to filter out bad coregistrations after coregistering all the target images to the template image.
- All of the bad coregistrations will be moved to a new directory called "failed_coregistration" that contains the bad coregistrations
- This creates a file called `filtered_files.csv` that contains a column called `filter_passed` that contains True if the image passed all the filtering steps
I recommend using these default settings.
```
filtering_settings = {
    'shift_reliability': 40,  # Default minimum threshold for shift reliability percentage. 
    'window_size': 50,  # Minimum size of the window used to calculate coregistration shifts in pixels (smaller is worse)
    'max_shift_meters': 250,  # Default maximum allowable shift in meters
    'filter_z_score': True,  # Flag to determine if z-score filtering should be applied
    'filter_z_score_filter_passed_only': False,  # Flag to apply z-score filtering only to data that has passed previous filters
    'z_score_threshold': 2  # Threshold for z-score beyond which data points are considered outliers
}
```

3. Choose a session directory to be the directory in `data` containing the tiffs, the location of the sorted jpgs, and the template file to coregister all the files in the session to

  - Replace the existing paths with the locations of your files
  - `template_path` : This is the tiff file that you want to coregister the target to.
  - `sorted_jpg_path` :This is the location to the RGB jpg files within the `session_dir` selected. Only the jpgs directly in this folder will be used to load the tif files to coregister.
  - `session_dir` : This is the directory of the ROI within CoastSeg's `data` folder that contains all the downloaded data.
  - Note: None of these files will be modified by the coregistration process. Any modifications will be saved to new directories and the finishes coregistered image will be saved out to the 'coregistered' directory

```
session_dir = r'C:\development\doodleverse\coastseg\CoastSeg\data\ID_1_datetime11-04-24__04_30_52_original_mess_with'
template_path = r"C:\development\doodleverse\coastseg\CoastSeg\data\ID_1_datetime11-04-24__04_30_52_original\L9\ms\2023-06-30-22-01-55_L9_ID_1_datetime11-04-24__04_30_52_ms.tif"
sorted_jpg_path = r'C:\development\doodleverse\coastseg\CoastSeg\data\ID_1_datetime11-04-24__04_30_52_original_mess_with\jpg_files\preprocessed\RGB'

```

4. Run the script
   - The coregistered images will be saved to 'coregistered' directory
   - A json file called `transformation_results.json` will be saved to the same directory.
   - A CSV file called `filtered_files.csv` will be saved to the same directory. This file contains whether each file passed outlier filtering or not in `filter_passed` column.
   - Below is an example of the `coregistered` folder generated by the tool. It mirrors the struture of the original session and has the coregisterd files for each satellite in the same organizational format as the original. 
![image](https://github.com/user-attachments/assets/5895e591-6706-4147-ada7-496b9710f132)

   - <bold> Example of one file's coregistration output from coreg_result.json </bold>
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

 ### Summary 
1. Uses the filenames in the `sorted_jpg_path` to load in the matching tiff files from the `ms` folder for each satellite for coregistration
2. Calculates the shifts needed to coregister each of the tiff files from the `ms` folder for each satellite.
 -  It saves a file containing all the files that were coregistered to `'transformation_results.json'`
- It saves all the coregistered file to a directory called `coregistered`
3. It filters all the files in the `'transformation_results.json'` files based on the `filter_settings` and moves files that failed filtered to `failed_coregistration` within the `coregistered` directory
4. It copies the `pan`,`nir`, and `mask` folders tiffs for the matching files that passed filtering and applies the shifts determined by coregisteration to them. These files are saved to the `coregistered` directory.
5. It creates new jpgs using the coregistered files and saves them to `jpg_files` in the `coregistered` directory. This is only for the files that passed filtering.
6. It updates the config.json file's `sitename` to be the location of the coregistered files so that coastseg reads the coregistered file from there.

![image](https://github.com/user-attachments/assets/7e39c956-63b3-432c-b160-5d2b367ff504)


</details>

# Filtering Guide
Outlier filtering is performed by reading the results of coregistering all the images in a dataset and filtering out bad shifts relative to the other files in the dataset.
To filter a dataset used the `filter_coregistration` function that takes the filter_settings as an input. The  `filter_coregistration` function will apply the filters in the order the settings are listed below:

1. **shift_reliability**: Filters out any images whole shift reliability, which is calculated during coregistration, is below this percentage. 
- Generally the lower this value is (40% or lower indicates that the coregistration was probably not successful and the shifts are incorrect)
2. **window_size** : Filters out any images whose window size used to coregister was below this size. Typically the smaller the window the less accurate the coregistration.
3. **max_shift_meters** : Filters out any images where the predicted shift to coregister the image to the target was above this value.
4. **z_score_threshold** : Filters out shifts by z score. The z score is the combined z score of the x and y pixel shifts for each image.
   - The combined z score = $$\sqrt{x_{\text{zscore}} + y_{\text{zscore}}}$$, where  $$x_{\text{zscore}}$$ z score of the x shift calculated during the coregistration process
   - If the combined z score exceeds the z_threshold then it is flagged as an outlier in the CSV generated by `apply_outliers`
   - **filter_z_score_filter_passed_only**: If this is set to True then only the images who have passed the previous filters will have their zscore calculated. This means that the zscore is calculated only using the best images up to this point.


# Credits
Thanks to [arosics](https://github.com/GFZ/arosics) for making this possible.
