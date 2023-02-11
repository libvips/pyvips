#!/usr/bin/python3

import sys
import pyvips

if len(sys.argv) < 3:
    print(f"usage: {sys.argv[0]} output-image frame1 frame2 ...")
    sys.exit(1)

# the input images
# assume these are all the same size
images = [pyvips.Image.new_from_file(filename, access="sequential")
          for filename in sys.argv[2:]]

animation = images[0].pagejoin(images[1:])

# frame delays are in milliseconds ... 300 is pretty slow!
delay_array = [300] * len(images)
animation.set_type(pyvips.GValue.array_int_type, "delay", delay_array)

print(f"writing {sys.argv[1]} ...")
animation.write_to_file(sys.argv[1])
