#!/usr/bin/python3
"""
example pyvips code to run thumbnail on a dir full of images

https://libvips.github.io/pyvips/vimage.html?highlight=thumbnail#pyvips.Image.thumbnail
"""

import os
import multiprocessing
import sys
import pyvips


def thumbnail(directory, filename):
    try:
        name, extension = os.path.splitext(filename)
        thumb = pyvips.Image.thumbnail(f"{directory}/{filename}", 128)
        thumb.write_to_file(f"{directory}/tn_{name}.jpg")
    except pyvips.Error:
        # ignore failures due to eg. not an image
        pass


def all_files(path):
    for (root, dirs, files) in os.walk(path):
        for file in files:
            yield root, file


with multiprocessing.Pool() as pool:
    pool.starmap(thumbnail, all_files(sys.argv[1]))
