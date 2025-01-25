# This script was written on 1/21/25
# By Sharon Batiste

# Example from global coregistration example on arosics documentation
# -----------------------------------
# from arosics import COREG

# im_reference = '/path/to/your/ref_image.bsq'
# im_target    = '/path/to/your/tgt_image.bsq'

# CR = COREG(im_reference, im_target, wp=(354223, 5805559), ws=(256,256))
# CR.calculate_spatial_shifts()
# -----------------------------------

# -------------
# Excerpt from the arosics documentation: https://danschef.git-pages.gfz-potsdam.de/arosics/doc/usage/input_data_requirements.html
# The no-data value of each image is automatically derived from the image corners. However, this may fail if the actual no-data value is not present within a 3x3 matrix at the image corners.
#  User provided no-data values will speed up the computation and avoid wrongly derived values.
# -------------

from helpers import *
from arosics_filter import *
import os
import glob
from tqdm import tqdm

# 1. Create a folder to save the coregistered images
output_folder = "coregistered_planet"
# This is the directory to save any of the targets that have been modified
modified_target_folder = "modified_targets"
modified_template_folder = "modified_templates"
rescaled_target_folder = "rescaled_targets"
  
os.makedirs(output_folder, exist_ok=True)
os.makedirs(modified_target_folder, exist_ok=True)
os.makedirs(rescaled_target_folder, exist_ok=True)
os.makedirs(modified_template_folder, exist_ok=True)

# Step 2a. Make a set of settings to coregitser the target to the reference
coregister_settings = {
    "ws": (256, 256), # window size
    "nodata":(0,0),
    "max_shift":100,
    "binary_ws":False, # This forces the window size to be a power of 2
    "progress":True,  # This shows the progress of the coregistration
    "v":False,         # This shows the verbose output
    "ignore_errors":True, # Useful for batch processing. In case of error COREG.success == False and COREG.x_shift_px/COREG.y_shift_px is None        
    "fmt_out": "GTiff",
}
# Step 2b. Make a set of settings to filter the coregistration results
filtering_settings = {
    'shift_reliability': 40,  # Default minimum threshold for shift reliability percentage. 
    'window_size': 50,  # Minimum size of the window used to calculate coregistration shifts in pixels (smaller is worse)
    'max_shift_meters': 250,  # Default maximum allowable shift in meters
    'filter_z_score': True,  # Flag to determine if z-score filtering should be applied
    'filter_z_score_filter_passed_only': False,  # Flag to apply z-score filtering only to data that has passed previous filters
    'z_score_threshold': 2  # Threshold for z-score beyond which data points are considered outliers
}

# Step 3. Define the reference and target images
im_reference = r"C:\3_code_from_dan\6_coregister_implementation_coastseg\raw_coastseg_data\L9\ms\2023-08-01-22-02-10_L9_ID_uxk1_datetime11-04-24__05_08_02_ms.tif"
target_folder = r'C:\development\coastseg-planet\downloads\UNALAKLEET_pier_cloud_0.7_TOAR_enabled_2020-06-01_to_2023-08-01\e2821741-0677-435a-a93a-d4f060f3adf4\PSScene'

# preprocess the reference image
modified_reference_path = os.path.join(modified_template_folder, os.path.basename(im_reference))
im_reference = update_nodata_value(im_reference, modified_reference_path, new_nodata=0)
os.makedirs("modified_targets", exist_ok=True)

# Step 4. Coregister the images in the target folder
# a. match files that match the pattern
pattern = '*MS_toar_clip.tif'
# get files that match the pattern with glob
tif_files = glob.glob(os.path.join(target_folder, pattern))
# b. coregister the files
coreg_results = coregister_files(tif_files,im_reference,output_folder,modified_target_folder,coregister_settings,desc="Coregistering Images")
# c. add the settings to the coreg_results under the key "coregister_settings"
coreg_results.append({"settings":coregister_settings})
#d. merge the list of dictionaries into a single dictionary
coreg_results = merge_list_of_dicts(coreg_results)


# Step 5. Save the coregistered Result to a json file
json_save_path = os.path.join(output_folder, "coreg_results.json")
print(f"Saving the coregistered results to {json_save_path}")
save_to_json(coreg_results, json_save_path)

#Step 6. Filter the coregistration results
csv_path = os.path.join(output_folder, "filtered_files.csv")
df = filter_coregistration(json_save_path,output_folder,csv_path,filtering_settings)
failed_coregs = list(df[~df['filter_passed']]['filename'].values)
print(f"length of failed coregs: {len(failed_coregs)}")

bad_folder = os.path.join(output_folder, "failed_coregistration")
os.makedirs(bad_folder, exist_ok=True)

failed_coregs = list(df[~df['filter_passed']]['filename'].values)
print(f"length of failed coregs: {len(failed_coregs)}")

move_files_to_folder(failed_coregs,output_folder,bad_folder,move_only=True)
