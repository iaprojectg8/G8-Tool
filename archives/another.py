from utils.imports import *
from PIL import Image

# Example raster data (2D array)
data = np.random.rand(100, 100) * 255  # Random raster data scaled to 0-255
data = data.astype(np.uint8)  # Convert to uint8 for image rendering

# Save raster as an image
image = Image.fromarray(data)
image_path = "raster_image.png"
image.save(image_path)

# Define the geographic bounds of the raster (latitude and longitude)
lat_min, lat_max = 10, 20
lon_min, lon_max = 30, 40

# Create the figure
fig = go.Figure()


# Add a map background or other traces
fig.add_trace(
    go.Scattermapbox()
)
print(lon_min, lon_max)
fig.add_layout_image(
    dict(
        source=image_path,
        x=lon_min,  # Minimum longitude
        y=lat_max,  # Maximum latitude
        xref="x",
        yref="y",
        sizex=lon_max - lon_min,  # Longitude span
        sizey=lat_max - lat_min,  # Latitude span
        xanchor="left",
        yanchor="top",
        layer="above",
    )
)

# Configure the mapbox layout
fig.update_layout(
    mapbox=dict(
        style="open-street-map",
        center={"lat": (lat_min + lat_max) / 2, "lon": (lon_min + lon_max) / 2},
        zoom=5,
    ),
    title="Raster Image with Flexible Background",

)

# Display the figure
st.plotly_chart(fig)
