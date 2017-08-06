#!/usr/bin/python

import sys

#import logging
#logging.basicConfig(level = logging.DEBUG)

import pyvips

a = pyvips.Image.new_from_file(sys.argv[1])

b = a.write_to_memory()

c = pyvips.Image.new_from_memory(b, a.width, a.height, a.bands, a.bandfmt)

c.write_to_file("x.v")
