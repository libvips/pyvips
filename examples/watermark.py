#!/usr/bin/python3

import sys
import pyvips

im = pyvips.Image.new_from_file(sys.argv[1], access="sequential")

text = pyvips.Image.text(sys.argv[3], width=500, dpi=300, align="centre")

# we make an overlay with a solid colour in the main image bands, and a faded
# version of the text mask as the overlay

# drop any alpha
if im.hasalpha():
    no_alpha = im.extract_band(0, n=im.bands - 1)
else:
    no_alpha = im

# colours have four parts in cmyk images
if im.bands == 4:
    text_colour = [0, 255, 0, 0]
elif im.bands == 3:
    text_colour = [255, 0, 0]
else:
    text_colour = 255

overlay = no_alpha.new_from_image(text_colour)
overlay = overlay.bandjoin((text * 0.5).cast("uchar"))

# position overlay at the bottom left, with a margin
im = im.composite(overlay, "over", x=100, y=im.height - text.height - 100)

im.write_to_file(sys.argv[2])
