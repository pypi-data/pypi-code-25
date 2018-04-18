import math
import random
from PIL import Image

def categorize_pixels(image, pixel_categorizer):
    image = load_image(image)
    pixels = image.getdata()
    pixel_map = {}
    for pixel in pixels:
        category = pixel_categorizer(*pixel)
        pixel_map[category] = pixel_map.get(category, 0) + 1
    return pixel_map

def load_image(image):
    return Image.open(image) if isinstance(image, str) else image

def image_average_color(image):
    image = load_image(image)
    pixels = image.getdata()
    count = 0
    red = 0
    green = 0
    blue = 0
    for pixel in pixels:
        red += pixel[0]
        green += pixel[1]
        blue += pixel[2]
        count += 1
    return (round(red/count), round(green/count), round(blue/count))

def chunkify_image(image, chunk_height, chunk_width=None):
    image = load_image(image)
    chunk_width = chunk_width if chunk_width else chunk_height
    height = image.height
    width = image.width
    chunks = []
    for h in range(math.ceil(height/chunk_height)):
        h1 = h * chunk_height
        h2 = min(height, (h+1) * chunk_height)
        for w in range(math.ceil(width/chunk_width)):
            w1 = w * chunk_width
            w2 = min(width, (w+1) * chunk_width)
            chunks.append(image.crop((w1, h1, w2, h2)))
    return chunks

def shufflechunk_image(image, chunk_height, chunk_width=None):
    image = load_image(image)
    chunk_width = chunk_width if chunk_width else chunk_height
    chunks = chunkify_image(image, chunk_height, chunk_width)
    random.shuffle(chunks)
    new_image = Image.new('RGB', (image.width, image.height))
    i = 0
    for h in range(math.ceil(new_image.height/chunk_height)):
        h1 = h * chunk_height
        for w in range(math.ceil(new_image.width/chunk_width)):
            w1 = w * chunk_width
            chunk = chunks[i]
            i += 1
            new_image.paste(chunk, (w1,h1))
    return new_image
    
