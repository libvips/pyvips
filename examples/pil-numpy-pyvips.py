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
# oh dear str lookup ... is there a better way?
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

# load with PIL
start_pillow = time.time()
pillow_img = np.asarray(Image.open(sys.argv[1]))
print('Pillow Time:', time.time()-start_pillow)
print('original shape', pillow_img.shape)

# load with vips to a memory array
start_vips = time.time()
img = pyvips.Image.new_from_file(sys.argv[1], access='sequential')
mem_img = img.write_to_memory()

# then make a numpy array from that buffer object
np_3d = np.ndarray(buffer=mem_img,
                   dtype=format_to_dtype[img.format],
                   shape=[img.height, img.width, img.bands])

print('Vips Time:', time.time()-start_vips)
print('final shape', np_3d.shape)

# verify we have the same result
print('Sum of the Differences:', np.sum(np_3d-pillow_img))

# make a vips image from the numpy array
height, width, bands = np_3d.shape
linear = np_3d.reshape(width * height * bands)
vi = pyvips.Image.new_from_memory(linear.data, width, height, bands,
                                  dtype_to_format[str(np_3d.dtype)])

# and write back to disc for checking
vi.write_to_file(sys.argv[2])
