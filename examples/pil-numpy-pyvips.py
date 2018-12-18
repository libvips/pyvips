#!/usr/bin/python3

import sys
import time

import pyvips
from PIL import Image
import numpy as np

if len(sys.argv) != 3:
    print('usage: {0} input-filename output-filename'.format(sys.argv[0]))
    sys.exit(-1)

# map vips formats to np dtypes
format_to_dtype = {
    'uchar': np.uint8,
    'char': np.int8,
    'ushort': np.uint16,
    'short': np.int16,
    'uint': np.uint32,
    'int': np.int32,
    'float': np.float32,
    'double': np.float64,
    'complex': np.complex64,
    'dpcomplex': np.complex128,
}

# map np dtypes to vips
dtype_to_format = {
    'uint8': 'uchar',
    'int8': 'char',
    'uint16': 'ushort',
    'int16': 'short',
    'uint32': 'uint',
    'int32': 'int',
    'float32': 'float',
    'float64': 'double',
    'complex64': 'complex',
    'complex128': 'dpcomplex',
}


# numpy array to vips image
def numpy2vips(a):
    height, width, bands = a.shape
    linear = a.reshape(width * height * bands)
    vi = pyvips.Image.new_from_memory(linear.data, width, height, bands,
                                      dtype_to_format[str(a.dtype)])
    return vi


# vips image to numpy array
def vips2numpy(vi):
    return np.ndarray(buffer=vi.write_to_memory(),
                      dtype=format_to_dtype[vi.format],
                      shape=[vi.height, vi.width, vi.bands])


# load with PIL
start_pillow = time.time()
pillow_img = np.asarray(Image.open(sys.argv[1]))
print('Pillow Time:', time.time() - start_pillow)
print('pil shape', pillow_img.shape)

# load with vips to a memory array
start_vips = time.time()
img = pyvips.Image.new_from_file(sys.argv[1])
np_3d = vips2numpy(img)

print('Vips Time:', time.time() - start_vips)
print('vips shape', np_3d.shape)

# make a vips image from the numpy array
vi = numpy2vips(pillow_img)

# verify we have the same result
# this can be non-zero for formats like jpg if the two libraries are using
# different libjpg versions ... try with png instead
print('Average pil/vips difference:', (vi - img).avg())

# and write back to disc for checking
vi.write_to_file(sys.argv[2])
