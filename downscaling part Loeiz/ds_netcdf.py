import xarray as xr
import numpy as np
import matplotlib.pyplot as plt
from scipy.stats import gamma, beta
import pandas as pd

# 🚀 Step 1: Load NetCDF Data
ds = xr.open_dataset("Prec-2025-01.nc")  # Replace with your actual NetCDF file

# 🚀 Step 2: Fix Time Dimension Name
if "valid_time" in ds.coords:
    ds = ds.rename({"valid_time": "time"})  # Rename valid_time to time

# Ensure time is in datetime64 format
ds["time"] = pd.date_range(start=ds["time"].values[0], periods=len(ds["time"]), freq="h")

# 🚀 Step 3: Define Enhanced Stochastic Multiplicative Cascade Model
def enhanced_multiplicative_cascade(hourly_rain, num_subdivisions=4, extreme_threshold=0.9):
    shape = hourly_rain.shape  
    hourly_rain_flat = hourly_rain.flatten()
    
    nonzero_rain = hourly_rain_flat[hourly_rain_flat > 0]
    extreme_threshold_value = np.percentile(nonzero_rain, extreme_threshold * 100) if len(nonzero_rain) > 0 else 0
    
    downscaled_rain = np.zeros((num_subdivisions, len(hourly_rain_flat)))  

    for i in range(len(hourly_rain_flat)):
        if hourly_rain_flat[i] == 0 or np.isnan(hourly_rain_flat[i]):  
            downscaled_rain[:, i] = 0  
        else:
            if hourly_rain_flat[i] >= extreme_threshold_value:
                shape_param = 2  
                scale_param = hourly_rain_flat[i] / shape_param  
                weights = gamma.rvs(shape_param, scale=scale_param, size=num_subdivisions)
            else:
                weights = beta.rvs(2, 2, size=num_subdivisions)

            if np.sum(weights) == 0:  # Ensure no division by zero
                weights = np.ones(num_subdivisions) / num_subdivisions  
            else:
                weights /= np.sum(weights)

            downscaled_rain[:, i] = hourly_rain_flat[i] * weights  

    return downscaled_rain.reshape((num_subdivisions,) + shape)

# 🚀 Step 4: Temporal Downscaling (Hourly → 15-min)
num_subdivisions = 4  # 4 intervals per hour (15-min resolution)
rain = ds["tp"]

# Generate new time coordinate with 15-min intervals
new_time = pd.date_range(start=ds["time"].values[0], periods=len(ds["time"]) * num_subdivisions, freq="15min")

# Perform linear interpolation to get 15-min time steps
rain_15min = rain.resample(time="15min").interpolate("linear")

# Apply improved stochastic downscaling while preserving spatial dimensions
downscaled_rain = np.array([
    enhanced_multiplicative_cascade(rain.isel(time=i).values) for i in range(len(rain.time))
])

# Reshape to match (new_time, lat, lon)
downscaled_rain = downscaled_rain.reshape((-1, *rain.shape[1:]))

# Convert back to xarray DataArray with the correct shape
rain_15min_downscaled = xr.DataArray(
    downscaled_rain,
    dims=["time", "latitude", "longitude"],
    coords={"time": new_time, "latitude": rain.latitude, "longitude": rain.longitude}
)

# 🚀 Step 5: Save Downscaled Data
rain_15min_downscaled.to_netcdf("enhanced_stochastic_rainfall_15min.nc")

print("✅ Advanced temporal downscaling completed successfully!")

# Load the temporally downscaled dataset (15-min resolution)
ds_15min = xr.open_dataset("enhanced_stochastic_rainfall_15min.nc")

# Define new higher-resolution lat/lon grid
new_lat = np.arange(ds_15min.latitude.min(), ds_15min.latitude.max(), 0.01)
new_lon = np.arange(ds_15min.longitude.min(), ds_15min.longitude.max(), 0.01)

# Apply bilinear interpolation for spatial downscaling
ds_15min_highres = ds_15min.interp(latitude=new_lat, longitude=new_lon, method="linear")

# Save the spatially downscaled dataset
ds_15min_highres.to_netcdf("rainfall_15min_0.05deg.nc")

print("✅ Spatial downscaling completed successfully! High-resolution dataset saved.")