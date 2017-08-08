#!/usr/bin/python3

import sys

import pyvips

# import logging
# logging.basicConfig(level = logging.DEBUG)

# pyvips.cache_set_trace(True)

a = pyvips.Image.new_from_file(sys.argv[1])

a = a[1:]

a.write_to_file(sys.argv[2])
