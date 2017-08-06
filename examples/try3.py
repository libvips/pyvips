#!/usr/bin/python

import sys

#import logging
#logging.basicConfig(level = logging.DEBUG)

import pyvips

pyvips.cache_set_trace(True)

a = pyvips.Image.new_from_file(sys.argv[1])
print a.max()
print a.max()

