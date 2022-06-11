#!/usr/bin/python3

import sys
import time

import pyvips
from PIL import Image
import numpy as np

if len(sys.argv) != 3:
    print('usage: {0} input-filename output-filename'.format(sys.argv[0]))
    sys.exit(-1)


# load with PIL
start_pillow = time.time()
pillow_img = np.asarray(Image.open(sys.argv[1]))
print('Pillow Time:', time.time() - start_pillow)
print('pil shape', pillow_img.shape)

# load with vips to a memory array
start_vips = time.time()
img = pyvips.Image.new_from_file(sys.argv[1])
np_3d = np.asarray(img)     # or img.numpy()

print('Vips Time:', time.time() - start_vips)
print('vips shape', np_3d.shape)

# make a vips image from the PIL image
vi = pyvips.Image.new_from_array(pillow_img)

# verify we have the same result
# this can be non-zero for formats like jpg if the two libraries are using
# different libjpg versions ... try with png instead
print('Average pil/vips difference:', (vi - img).avg())

# and write back to disc for checking
vi.write_to_file(sys.argv[2])
