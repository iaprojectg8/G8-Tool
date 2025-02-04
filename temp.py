from qgis.core import QgsProject, QgsRasterLayer, QgsLayerTreeGroup

# Path to your multi-band raster file
raster_path = 'C:/Users/FlorianBERGERE/Downloads/Days above 35°C(6).tif'

# Load the raster layer
raster_layer = QgsRasterLayer(raster_path, 'Multi-band Raster')

if not raster_layer.isValid():
    print("Failed to load the raster layer!")
else:
    # Create a new group in the layer tree
    root = QgsProject.instance().layerTreeRoot()
    group = root.addGroup('Raster Bands')

    # Add each band as a separate layer in the group
    for band in range(1, raster_layer.bandCount() + 1):
        single_band_layer = QgsRasterLayer(raster_path, f'Band {band}', 'gdal', band)
        if single_band_layer.isValid():
            QgsProject.instance().addMapLayer(single_band_layer, False)
            group.addLayer(single_band_layer)
        else:
            print(f"Failed to load band {band}!")

    print("Raster bands added to the group successfully!")