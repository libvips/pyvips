#!/usr/bin/python3

import sys
import pyvips

im = pyvips.Image.new_from_file(sys.argv[1], access="sequential")

text = pyvips.Image.text(f"<span color=\"red\">{sys.argv[3]}</span>",
                         width=500,
                         dpi=100,
                         align="centre",
                         rgba=True)

# scale the alpha down to make the text semi-transparent
text = (text * [1, 1, 1, 0.3]).cast("uchar")

text = text.rotate(45)

# tile to the size of the image page, then tile again to the full image size
text = text.embed(10, 10, text.width + 20, text.width + 20)
page_height = im.get_page_height()
text = text.replicate(1 + im.width / text.width, 1 + page_height / text.height)
text = text.crop(0, 0, im.width, page_height)
text = text.replicate(1, 1 + im.height / text.height)
text = text.crop(0, 0, im.width, im.height)

# composite the two layers
im = im.composite(text, "over")

im.write_to_file(sys.argv[2])
