#!/usr/bin/python3

import sys
import pyvips

if len(sys.argv) != 3:
    print(f"usage: {sys.argv[0]} output-directory animated-image")
    sys.exit(1)

# load the animation, chop into pages
image = pyvips.Image.new_from_file(sys.argv[2], n=-1, access="sequential")

delay = image.get("delay")
print(f"delay array = {delay}")

pages = image.pagesplit()
print(f"writing frames to {sys.argv[1]}/ ...")
for page_number in range(len(pages)):
    filename = f"{sys.argv[1]}/frame-{page_number:04}.tif"
    pages[page_number].write_to_file(filename)
