#!/usr/bin/python

import sys
# import logging
import pyvips

# logging.basicConfig(level = logging.DEBUG)

a = pyvips.Image.new_from_array([[1, 2, 3], [4, 5, 6], [7, 8, 9]], 8, 128)

print 'scale =', a.get('scale')
print 'offset =', a.get('offset')

a.write_to_file("x.v")
