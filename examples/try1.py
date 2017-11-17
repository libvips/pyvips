#!/usr/bin/env python

import logging
logging.basicConfig(level = logging.DEBUG)

import pyvips

print('test Image')
image = pyvips.Image.new_from_file('/data/john/pics/k2.jpg')
print('image =', image)
print('image.width =', image.width)
print('\n''')
