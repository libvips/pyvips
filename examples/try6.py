#!/usr/bin/python

import sys
# import logging
import pyvips

# logging.basicConfig(level = logging.DEBUG)

a = pyvips.Image.new_from_file(sys.argv[1])

b = a.write_to_buffer(".jpg")

c = pyvips.Image.new_from_buffer(b, "")
