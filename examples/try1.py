#!/usr/bin/env python

import pyvips

print('test Image')
image = pyvips.Image.new_from_file('/home/john/pics/k2.jpg')
print('image =', image)
print('image.width =', image.width)
print('\n''')

print('test Operation')
image2 = pyvips.Operation.call('embed', image, 1, 2, 3, 4, extend='copy')
print('image2 =', image2)
print('\n''')
print('test getattr')
image2 = image.embed(1, 2, 3, 4, extend='copy')
print('image2 =', image2)
print('\n''')
