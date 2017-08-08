#!/usr/bin/python

import sys

# import logging
# logging.basicConfig(level = logging.DEBUG)

import pyvips

# pyvips.cache_set_trace(True)

a = pyvips.Image.new_from_file(sys.argv[1])

profile = a.get_value("icc-profile-data")

with open('x.icm', 'w') as f:
    f.write(profile)
