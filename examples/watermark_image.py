#!/usr/bin/python3

import sys
import pyvips

image = pyvips.Image.new_from_file(sys.argv[1], access="sequential")
watermark = pyvips.Image.new_from_file(sys.argv[3], access="sequential")

# downsize the image by 50%
image = image.resize(0.5)

# set the watermark alpha to 20% (multiply A of RGBA by 0.2).
watermark *= [1, 1, 1, 0.2]

# overlay the watermark at the bottom left, with a 100 pixel margin
image = image.composite(watermark, "over",
                        x=100, y=image.height - watermark.height - 100)

image.write_to_file(sys.argv[2])
