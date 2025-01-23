import xarray as xr
import os
from utils.variables import *
import pandas as pd
from tqdm import tqdm
import shutil

def process_nc_file_to_dataframe(nc_file_path):
    """
    Process a NetCDF file and convert it into a DataFrame.

    Args:
        nc_file_path (str): The path to the NetCDF file.

    Returns:
        pd.DataFrame: The processed data as a DataFrame.
    """
    # Open the NetCDF file using xarray
    ds = xr.open_dataset(nc_file_path, engine="netcdf4")
    df = ds.to_dataframe().reset_index()

    # Change the name of the time columns to date to correspond to the future processing
    df.rename(columns={"time": "date"}, inplace=True)
    df.set_index(["date", "lat", "lon"], inplace=True)
    # Sort the data we have to get the right order in terms of date
    df.sort_index(inplace=True)
    print(df)
    return df

def save_dataframe_to_csv(df, csv_file_path):
    """
    Save a DataFrame to a CSV file.

    Args:
        df (pd.DataFrame): The DataFrame to save.
        csv_file_path (str): The path to the CSV file.
    """
    df.to_csv(csv_file_path, index=True)

def process_all_nc_files(nc_file_dir, csv_file_dir, years=list(range(1950, 2015))):
    """
    Process all NetCDF files in a directory and save them as CSV files.

    Args:
        nc_file_dir (str): The directory containing the NetCDF files.
        csv_file_dir (str): The directory to save the CSV files.
    """
    # Ensure the CSV directory exists
    
    # Loop through all NetCDF files in the directory
    whole_df = pd.DataFrame()
    for year in tqdm(years):
        whole_year_df = pd.DataFrame()
        for nc_file in os.listdir(nc_file_dir):
            if str(year) in nc_file and nc_file.endswith(".nc"):
                nc_file_path = os.path.join(nc_file_dir, nc_file)

                # Process the NetCDF file to a DataFrame
                df = process_nc_file_to_dataframe(nc_file_path)
                whole_year_df=pd.concat([whole_year_df, df], ignore_index=False, axis=1)

        whole_df = pd.concat([whole_df, whole_year_df], ignore_index=False, axis=0)  
    for (lat, lon), group_df in whole_df.groupby(['lat', 'lon']):
        # Create filename using lat/lon
        filename = f"lat_{lat}_lon_{lon}.csv"
        csv_file_path = os.path.join(csv_file_dir, filename)
        
        # Save individual lat/lon DataFrame to CSV
        save_dataframe_to_csv(group_df, csv_file_path)
        print(f"Saved {csv_file_path}")


def zip_csv_files(csv_dir, zip_name):
    """
    Zip all CSV files in the directory
    """
    # Create zip file
    shutil.make_archive(zip_name, 'zip', csv_dir)
    return f"{zip_name}.zip"

# Example usage
process_all_nc_files(NC_FILE_DIR, CSV_FILE_DIR)
# Custom the name of the zip file in order to avoid user not knowing what he is downloading
zip_csv_files(CSV_FILE_DIR, "csv_files")