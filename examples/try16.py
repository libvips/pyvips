#!/usr/bin/python3

import sys

import logging
logging.basicConfig(level = logging.DEBUG)

import pyvips

# pyvips.cache_set_trace(True)

a = pyvips.Image.new_from_file(sys.argv[1])

x = a.erode([[128, 255, 128], 
             [255, 255, 255],
             [128, 255, 128]])

x.write_to_file(sys.argv[2])


