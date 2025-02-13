from PIL import Image

def convert_jpeg_to_png_with_transparency(jpeg_path, png_path, background_color=(255, 255, 255)):
    """
    Convert a JPEG image with a solid background to a PNG with a transparent background.

    Args:
        jpeg_path (str): Path to the input JPEG file.
        png_path (str): Path to save the output PNG file.
        background_color (tuple): RGB color of the background to be made transparent.
    """
    # Open the JPEG image
    img = Image.open(jpeg_path).convert("RGBA")

    # Get data of the image
    data = img.getdata()

    # Create a new list to hold the modified image data
    new_data = []
    for item in data:
        # Change all white (also shades of whites)
        # pixels to transparent
        if item[:3] == background_color:
            new_data.append((255, 255, 255, 0))
        else:
            new_data.append(item)

    # Update image data
    img.putdata(new_data)

    # Save as PNG
    img.save(png_path, "PNG")

# Example usage
jpeg_path = "logos/tool_logo.png"
png_path = "logos/new_tool_logo.png"
convert_jpeg_to_png_with_transparency(jpeg_path, png_path)