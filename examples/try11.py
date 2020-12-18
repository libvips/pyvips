#!/usr/bin/python3

import sys
import pyvips

# import logging
# logging.basicConfig(level = logging.DEBUG)

a = pyvips.Image.new_from_file(sys.argv[1])
ipct = a.get("ipct-data")
print("ipct = ", ipct.get())
a.remove("ipct-data")
a.write_to_file("x.jpg")
