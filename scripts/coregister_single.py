# This script was written on 1/27/25
# By Sharon Batiste

# Example script to coregister a single image to a reference image.

# This script saves the coregistered image to a folder called "coregistered" and the modified target images to a folder called "modified_targets"

# -------------

from helpers import *
import file_utilites as file_utils
from arosics_filter import *
import os

# 1. Create a folder to save the coregistered images
output_folder = "coregistered"
# This is the directory to save any of the targets that have been modified
modified_target_folder = "modified_targets"
modified_template_folder = "modified_templates"
rescaled_target_folder = "rescaled_targets"
  
os.makedirs(output_folder, exist_ok=True)
os.makedirs(modified_target_folder, exist_ok=True) # This is the directory to save any of the targets that have been modified
os.makedirs("modified_targets", exist_ok=True)
os.makedirs(rescaled_target_folder, exist_ok=True)
os.makedirs(modified_template_folder, exist_ok=True)

# Step 2a. Make a set of settings to coregitser the target to the reference
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

# Step 3. Define the reference and target images
im_reference = "sample_data/2023-06-30-22-01-55_L9_ms.tif"
im_target = "sample_data/2023-10-09-22-28-02_S2_ms.tif" # This is the image that will be coregistered to the reference image

# preprocess the reference image
modified_reference_path = os.path.join(modified_template_folder, os.path.basename(im_reference))
# arosics cannot handle -inf as a no data value so we set it to 0 (Note make sure that this matches the no data value in the coregister settings)
im_reference = update_nodata_value(im_reference, modified_reference_path, new_nodata=0)

# Step 4. Coregister the images in the target folder
coreg_result =coregister_file(im_reference,im_target,output_folder,modified_target_folder,coregister_settings)
coreg_result.update({"settings":coregister_settings})

# Step 5. Save the coregistered Result to a json file
json_save_path = os.path.join(output_folder, "coreg_result.json")
print(f"Saving the coregistered results to {json_save_path}")
save_to_json(coreg_result, json_save_path)


# Step 6. Clean Up 
# Remove the modified reference image and the modified target image
file_utils.delete_like_file(file_utils.get_root_name(im_target),modified_target_folder)
file_utils.delete_like_file(file_utils.get_root_name(im_target),rescaled_target_folder)
file_utils.delete_like_file(file_utils.get_root_name(im_reference),modified_template_folder)