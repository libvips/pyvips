#!/usr/bin/python3

import sys
import pyvips

# the input images
# assume these are all the same size
images = [pyvips.Image.new_from_file(filename, access="sequential") 
          for filename in sys.argv[2:]]

# frame delays are in milliseconds
delay_array = [300] * len(images)

animation = pyvips.Image.arrayjoin(images, across=1)
animation.set_type(pyvips.GValue.gint_type, "page-height", images[0].height)
animation.set_type(pyvips.GValue.array_int_type, "delay", delay_array)
print(f"writing {sys.argv[1]} ...")
animation.write_to_file(sys.argv[1])
