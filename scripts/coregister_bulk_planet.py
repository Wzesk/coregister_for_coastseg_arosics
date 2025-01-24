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
import arosics
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

# Step 2. Make a set of settings to coregitser the target to the reference
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

# Step 3. Define the reference and target images
im_reference = r"C:\3_code_from_dan\6_coregister_implementation_coastseg\raw_coastseg_data\L9\ms\2023-08-01-22-02-10_L9_ID_uxk1_datetime11-04-24__05_08_02_ms.tif"
target_folder = r'C:\development\coastseg-planet\downloads\UNALAKLEET_pier_cloud_0.7_TOAR_enabled_2020-06-01_to_2023-08-01\e2821741-0677-435a-a93a-d4f060f3adf4\PSScene'

# preprocess the reference image
modified_reference_path = os.path.join(modified_template_folder, os.path.basename(im_reference))
im_reference = update_nodata_value(im_reference, modified_reference_path, new_nodata=0)


os.makedirs("modified_targets", exist_ok=True)

# match files that match the pattern
pattern = '*MS_toar_clip.tif'
# get files that match the pattern with glob
tif_files = glob.glob(os.path.join(target_folder, pattern))
# store the results of all the coregistration in the list
coreg_results = []

for tif_file in tqdm(tif_files,desc="Coregistering Images"):
    coreg_result = {os.path.basename(tif_file): make_coreg_info()}

    # Step 1. If the crs is not the same for the reference and the target, skip the coregistration
    if not check_crs(im_reference, tif_file,raise_error=False):
        print("Cannot coregister images with different CRS")
        continue

    # Step 2. Read the current no data value of the target and convert it to a valid no data value
    #    - Invalid No Data Values : -inf, inf
    modified_target_path = os.path.join(modified_target_folder, os.path.basename(tif_file))
    im_target = update_nodata_value(tif_file, modified_target_path, new_nodata=0)

    # Step 3. Coregister the target to the reference
    result = coregister_image(im_reference, im_target,output_folder,coregister_settings,verbose=True)
    coreg_results.append(result)

# add the settings to the coreg_results under the key "coregister_settings"
coreg_results.append({"settings":coregister_settings})

# turn the list into a dictionary
def merge_list_of_dicts(list_of_dicts):
    merged_dict = {}
    for d in list_of_dicts:
        merged_dict.update(d)
    return merged_dict

coreg_results = merge_list_of_dicts(coreg_results)
print(coreg_results)

# Step 5. Save the coregistered Result to a json file
json_save_path = os.path.join(output_folder, "coreg_results.json")
print(f"Saving the coregistered results to {json_save_path}")
save_to_json(coreg_results, json_save_path)

#Step 6. Filter the coregistration results
df = filter_coregistration(json_save_path,output_folder)
failed_coregs = list(df[~df['filter_passed']]['filename'].values)
print(f"length of failed coregs: {len(failed_coregs)}")

bad_folder = os.path.join(output_folder, "failed_coregistration")
os.makedirs(bad_folder, exist_ok=True)

failed_coregs = list(df[~df['filter_passed']]['filename'].values)
print(f"length of failed coregs: {len(failed_coregs)}")

move_files_to_folder(failed_coregs,output_folder,bad_folder,move_only=True)
