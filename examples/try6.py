#!/usr/bin/python

import sys

#import logging
#logging.basicConfig(level = logging.DEBUG)

import pyvips

a = pyvips.Image.new_from_file(sys.argv[1])

b = a.write_to_buffer(".jpg")

c = pyvips.Image.new_from_buffer(b, "")
