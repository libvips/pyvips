#!/usr/bin/python3

import sys
import pyvips

input_file = open(sys.argv[1], "rb")


def read_handler(size):
    return input_file.read(size)


def seek_handler(offset, whence):
    input_file.seek(offset, whence)
    return input_file.tell()


source = pyvips.SourceCustom()
source.on_read(read_handler)
source.on_seek(seek_handler)

output_file = open(sys.argv[2], "wb")


def write_handler(chunk):
    return output_file.write(chunk)


def finish_handler():
    output_file.close()


target = pyvips.TargetCustom()
target.on_write(write_handler)
target.on_finish(finish_handler)

image = pyvips.Image.new_from_source(source, '', access='sequential')
image.write_to_target(target, '.png')
