#!/usr/bin/python3

import sys
import pyvips

# import logging
# logging.basicConfig(level = logging.DEBUG)

a = pyvips.Image.new_from_file(sys.argv[1])

b = pyvips.Image.new_from_file(sys.argv[2])

c = a.join(b, pyvips.Direction.HORIZONTAL,
           expand=True,
           shim=100,
           align=pyvips.Align.CENTRE,
           background=[128, 255, 128])

c.write_to_file(sys.argv[3])
