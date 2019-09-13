#!/usr/bin/python3
 
import sys
import pyvips
 
im = pyvips.Image.new_from_file(sys.argv[1], access="sequential")
 
text = pyvips.Image.text(sys.argv[3], width=500, dpi=300, align="centre")
text = (text * 0.3).cast("uchar")
text = text.rotate(45)
text = text.embed(100, 100, text.width + 200, text.width + 200)
text = text.replicate(1 + im.width / text.width, 1 + im.height / text.height)
text = text.crop(0, 0, im.width, im.height)

# we want to blend into the visible part of the image and leave any alpha
# channels untouched ... we need to split im into two parts
if im.hasalpha():
    alpha = im.extract_band(im.bands - 1)
    im = im.extract_band(0, n=im.bands - 1) 
else:
    alpha = None

# colours have four parts in cmyk images
if im.bands == 4:
    text_colour = [0, 255, 0, 0]
elif im.bands == 3:
    text_colour = [255, 0, 0]
else:
    text_colour = 255

im = text.ifthenelse(text_colour, im, blend=True)

# reattach alpha
if alpha:
    im = im.bandjoin(alpha)
 
im.write_to_file(sys.argv[2])
