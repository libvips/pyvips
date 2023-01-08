#!/usr/bin/python3

import sys

# uncomment to see startup log for pyvips
# import logging
# logging.basicConfig(level=logging.DEBUG)

import pyvips


print('test Image')
image = pyvips.Image.new_from_file(sys.argv[1])
print('image =', image)
print('image.width =', image.width)
print('\n''')
