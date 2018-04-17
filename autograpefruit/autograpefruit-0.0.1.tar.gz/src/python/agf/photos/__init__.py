from PIL import Image

def categorize_pixels(path_to_file, pixel_categorizer):
    img = Image.open(path_to_file)
    pixels = img.getdata()
    pixel_map = {}
    for pixel in pixels:
        category = pixel_categorizer(*pixel)
        pixel_map[category] = pixel_map.get(category, 0) + 1
    return pixel_map
