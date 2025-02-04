from utils.imports import *

def display_raster_with_slider(raster_path):
    """
    Display a multi-band raster with a slider to switch between epochs using Plotly.

    Args:
        raster_path (str): Path to the raster file.
    """
    # Open the raster file
    with rasterio.open(raster_path) as src:
        bands = src.read()
        epochs = [f"Epoch {i+1}" for i in range(bands.shape[0])]  # Create epoch labels

        # Find the min and max values directly from the raster data
        data_min = 1
        data_max = 4  # Use actual max value in data

    # Create a slider-based visualization without normalizing the data
    fig = px.imshow(
        bands[0],  # Initial band for display
        # animation_frame=
        color_continuous_scale=["green", "yellow", "orange","red"],  # Choose your preferred colormap
        zmin=data_min,  # Use the actual min value from the data
        zmax=data_max,  # Use the actual max value from the data
        title="Raster Visualization",
    )

    # Add a slider for epochs
    steps = []
    for i, band in enumerate(bands):
        step = {
            "args": [{"z": [band]}],
            "label": epochs[i],
            "method": "update",
        }
        steps.append(step)

    sliders = [
        {
            "active": 0,
            "currentvalue": {"prefix": "Epoch: "},
            "pad": {"t": 50},
            "steps": steps,
        }
    ]
    fig.update_layout_images()
    fig.update_layout(
        sliders=sliders,
        height=900 
    )

    # Display the map in Streamlit
    st.plotly_chart(fig, use_container_width=True)
    fig.write_image("whatever.png")

# Streamlit app
def display_raster():
    
    # Save the file locally
    raster_path = "another.tif"
    display_raster_with_slider(raster_path)

display_raster()