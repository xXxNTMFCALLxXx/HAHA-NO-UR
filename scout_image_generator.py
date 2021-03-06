import os
import shutil
import urllib
import requests
import aiohttp
import posixpath
from PIL import Image

IDOL_IMAGES_PATH = "idol_images/"
OUTPUT_PATH = "scout_output/"
CIRCLE_DISTANCE = 10

'''
Creates a stitched together image of idol circles.

idol_circles: List - urls of idol circle images to be stitched together
num_rows: Integer - Number of rows to use in the image
output_filename: String - name of output image file

return: String - path pointing to created image.
'''
async def create_image(idol_circle_urls, num_rows, output_filename):
    image_filepaths = [] # list of image filepaths

    # Save images that do not exists
    for image_url in idol_circle_urls:
        url_path = urllib.parse.urlsplit(image_url).path
        filename = posixpath.basename(url_path)
        image_filepaths.append(IDOL_IMAGES_PATH + filename)

        await download_image_from_url(image_url, IDOL_IMAGES_PATH + filename)

    # Load images
    circle_images = []
    for image_filepath in image_filepaths:
        circle_images.append(Image.open(image_filepath))

    image = await build_image(circle_images, num_rows, 10, 10)
    image.save(OUTPUT_PATH + output_filename, "PNG")

    return OUTPUT_PATH + output_filename

'''
Downloads an image from a url and saves it to a specified location

url: String - url of image
path: String - path where the image will be saved to
'''
async def download_image_from_url(url, path):
    # Create directories for storing images if they do not exist
    ensure_path_exists(IDOL_IMAGES_PATH)
    ensure_path_exists(OUTPUT_PATH)

    if not os.path.exists(path):
        print("Saving " + url + " to " + path)
        fp = open(path, "wb")
        response = await aiohttp.get(url)
        image = await response.read()
        fp.write(image)
        fp.close()

    return path

'''
Stitches together a list of images to an output image.

circle_images: Object - list of image object being stitched together
num_rows: Integer - number of rows to lay the image out in
x_distance: Integer - x spacing between each image
y_distane: Integer - y spacing between each image

return: Object - ouput image object
'''
async def build_image(circle_images, num_rows, x_distance, y_distance):
    # Compute required height and width
    circle_width, circle_height = circle_images[0].size
    out_height = num_rows * (circle_height + y_distance)
    out_width = ((len(circle_images) + 1) * (circle_width + x_distance)) // 2

    image = Image.new("RGBA", (out_width, out_height))

    circle_rows = []
    for row_index in range(0, num_rows):
        circle_rows.append([])

    i = 0
    for circle_image in circle_images:
        circle_rows[i % len(circle_rows)].append(circle_image)
        i += 1

    x = 0
    y = 0
    for row_index in range(0, len(circle_rows)):
        x = 0

        # Offset row
        if (row_index + 1) % 2 == 0:
            x += circle_width // 2

        for col_index in range(0, len(circle_rows[row_index])):
            image.paste(circle_rows[row_index][col_index], (x, y))
            x += circle_width + x_distance

        y += circle_height + y_distance

    return image

'''
Makes sure a path exists. Creates new directory if it does not.

path: String - path being checked
'''
def ensure_path_exists(path):
    try:
        os.mkdir(path)
    except OSError as Exception:
        return
