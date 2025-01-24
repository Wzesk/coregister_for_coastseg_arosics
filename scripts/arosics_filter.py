import pandas as pd
import os
import geopandas as gpd
import json
import numpy as np
import filters



# convert dict to dataframe
def coreg_dict_to_dataframe(dict_data):
    if "settings" in dict_data.keys():
        dict_data.pop("settings")

    try:
        df = filters.create_dataframe_with_satellites(dict_data)
    except Exception as e:
        df = pd.DataFrame(dict_data)
        # Flips the dataframe so that the image names are the rows and the columns are the values
        df = df.transpose()

    # Modify DataFrame structure
    df['filename'] = df.index
    df.reset_index(drop=True, inplace=True)
    df = df[['filename'] + [col for col in df.columns if col != 'filename']]
    return df

def filter_out_nones(df, col_name:str = 'coregistered_ssim'):
    if 'filter_passed' not in df.columns:
        df['filter_passed'] = True
    
    df['filter_passed'] = df.apply(
    lambda row: False if row[col_name] is None else row['filter_passed'], axis=1
    )
    return df
    
def filter_by_shift_reliability(df, col_name:str = 'shift_reliability', threshold:float = 40):
    if 'filter_passed' not in df.columns:
        df['filter_passed'] = True
    

    df['filter_passed'] = df.apply(
        lambda row: False if row[col_name] is None or row[col_name] < threshold else row['filter_passed'], axis=1
    )
    return df

    
def filter_by_max_shift_meters(df, threshold: float = 200):
    if 'filter_passed' not in df.columns:
        df['filter_passed'] = True

    df['filter_passed'] = np.where(
        (df['shift_x_meters'] > threshold) | (df['shift_x_meters'].isnull()) |
        (df['shift_y_meters'] > threshold) | (df['shift_y_meters'].isnull()),
        False,
        df['filter_passed']
    )
    return df



def filter_window_size(df, col_name:str = 'window_size', threshold:int = 50):
    if 'filter_passed' not in df.columns:
        df['filter_passed'] = True

    df['filter_passed'] = np.where(
        (df[col_name].apply(lambda x: x[0]) < threshold) | 
        (df[col_name].apply(lambda x: x[1]) < threshold),
        False,
        df['filter_passed']
    )
    return df

# OLD CODE
# def filter_by_zscore(df,zscore_threshold:float = 2,combined_z_plot_filename: str = 'combined_z_scores.png', shifts_plot_filename: str = 'plot_outlier_shifts.png'):
#     """
#     Identify and plot outliers, add combined z-scores to the DataFrame, and plot the shifts.

#     Args:
#         df (pd.DataFrame): DataFrame containing 'shift_x' and 'shift_y' columns.
#         z_threshold (float, optional): The z-score threshold to identify outliers. Defaults to 2.
#         combined_z_plot_filename (str, optional): The filename to save the combined z-scores plot. Defaults to 'combined_z_scores.png'.
#         shifts_plot_filename (str, optional): The filename to save the shifts plot. Defaults to 'plot_outlier_shifts.png'.

#     Returns:
#         pd.DataFrame: The updated DataFrame with combined z-scores added as a column.
#     """
#     df['shift_x'] = pd.to_numeric(df['shift_x'])
#     df['shift_y'] = pd.to_numeric(df['shift_y'])
#     df = filters.filter_by_z_score(df,zscore_threshold,combined_z_plot_filename,shifts_plot_filename)
#     return df

def filter_coregistration(results_path,output_folder, filter_settings: dict={}):
    # read in the results
    with open(results_path, 'r') as f:
        results = json.load(f)

    df = coreg_dict_to_dataframe(results)

    shift_reliability_threshold = filter_settings.get('shift_reliability',None)
    window_size_threshold = filter_settings.get('window_size',None)
    max_shift_meters_threshold = filter_settings.get('max_shift_meters',None)
    filter_z_score = filter_settings.get('filter_z_score',False)
    z_threshold = filter_settings.get('z_score_threshold',2)
    filter_z_score_filter_passed_only = filter_settings.get('filter_z_score_filter_passed_only',False)

    # apply the filters
    df = filter_out_nones(df)

    if shift_reliability_threshold:
        df = filter_by_shift_reliability(df,threshold=shift_reliability_threshold)

    if window_size_threshold:
        df = filter_window_size(df,threshold=window_size_threshold)

    if max_shift_meters_threshold:
        df = filter_by_max_shift_meters(df,threshold=max_shift_meters_threshold)

    if filter_z_score:
        # If filter_passed is True then the zscore will only be calculated for the passed images
        df = filters.filter_zscores(df, z_threshold=z_threshold, filter_passed_only=filter_z_score_filter_passed_only)
    
    csv_path = os.path.join(output_folder, "filtered_coreg_results.csv")
    df.to_csv(csv_path,index=False)
    print(f"Filtered coregistration results saved to {csv_path}")
    
    return df
