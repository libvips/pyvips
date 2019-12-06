#!/usr/bin/env python

import sys
import pyvips

input_file = open(sys.argv[1], "rb")


def read_handler(size):
    return input_file.read(size)


def seek_handler(offset, whence):
    input_file.seek(offset, whence)
    return input_file.tell()


input_stream = pyvips.Streamiu()
input_stream.on_read(read_handler)
input_stream.on_seek(seek_handler)

output_file = open(sys.argv[2], "wb")


def write_handler(chunk):
    return output_file.write(chunk)


def finish_handler():
    output_file.close()


output_stream = pyvips.Streamou()
output_stream.on_write(write_handler)
output_stream.on_finish(finish_handler)

image = pyvips.Image.new_from_stream(input_stream, '', access='sequential')
image.write_to_stream(output_stream, '.png')
