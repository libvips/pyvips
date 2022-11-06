#!/usr/bin/python3

import sys
import pyvips

# load the animation, chop into pages
image = pyvips.Image.new_from_file(sys.argv[2], n=-1, access="sequential")
page_height = image.get("page-height")
n_pages = image.get("n-pages")
delay = image.get("delay")
print(f"delay array = {delay}")

pages = [image.crop(0, page_number * page_height, image.width, page_height) 
         for page_number in range(0, n_pages)]
print(f"writing frames to {sys.argv[1]} ...")
for page_number in range(len(pages)):
    filename = f"{sys.argv[1]}/frame-{page_number:04}.tif"
    pages[page_number].write_to_file(filename)
