#!/usr/bin/python3

import logging
import pyvips

logging.basicConfig(level=logging.DEBUG)

print('test Image')
image = pyvips.Image.new_from_file('/data/john/pics/k2.jpg')
print('image =', image)
print('image.width =', image.width)
print('\n''')
