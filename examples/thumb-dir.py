#!/usr/bin/env python3
"""
example pyvips code to run thumbnail on a dir full of images

https://libvips.github.io/pyvips/vimage.html?highlight=thumbnail#pyvips.Image.thumbnail
process all images in a dir and put results in another dir
resize to fixed values for simplicity and only process jpg tif png
"""

import os
import sys
import pyvips

def resize(filein, fileout, maxw, maxh):
    im = pyvips.Image.new_from_file(filein, access="sequential")
    out = pyvips.Image.thumbnail(filein, maxw, height=maxh)
    out.write_to_file(fileout , Q=95)

# check dir dir args
if os.path.isdir(sys.argv[1]) and os.path.isdir(sys.argv[2]):
    # process all from one dir to the other
    srcdir = sys.argv[1]
    dstdir = sys.argv[2]
    files = os.listdir(srcdir)
    for fname in files:
       if fname.endswith( ('.jpg', '.tif', '.png') ) :
           resize(srcdir + "/" + fname, dstdir + "/" + fname, 128,128)

else:
    print("args: input dir, outputdir")
	

