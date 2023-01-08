#!/usr/bin/env python3
""" example pyvips code to convolve an image with a 3x3 mask

args: inputfile outputfile
no error checking for simplicity
Notes: the convolution mask can be other sizes,
here we use a scale of 1 (no scaling - see libvips conv docs)
https://www.libvips.org/API/current/libvips-convolution.html#vips-conv
and offset of 128 so zero output is mid-grey
"""
import pyvips
import sys

image = pyvips.Image.new_from_file(sys.argv[1], access='sequential')
mask = pyvips.Image.new_from_array([[1, 1, 1],
                                    [1, -8, 1],
                                    [1, 1, 1]
                                    ], scale=1, offset=128)
image = image.conv(mask, precision='integer')
image.write_to_file(sys.argv[2])
