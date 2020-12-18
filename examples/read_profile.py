#!/usr/bin/python3

import sys
import pyvips

# import logging
# logging.basicConfig(level = logging.DEBUG)
# pyvips.cache_set_trace(True)

a = pyvips.Image.new_from_file(sys.argv[1])

profile = a.get("icc-profile-data")

with open('x.icm', 'w') as f:
    f.write(profile)
