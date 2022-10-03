#!/usr/bin/python3

import sys
import pyvips

if len(sys.argv) != 4:
    print(f"usage: {sys.argv[0]} IN-FILE OUT-FILE FORMAT")
    print(f"   eg.: {sys.argv[0]} ~/pics/k2.jpg x .tif[tile]")
    sys.exit(1)


def source_custom(filename):
    input_file = open(sys.argv[1], "rb")

    def read_handler(size):
        return input_file.read(size)

    # seek is optional, but may improve performance by reducing buffering
    def seek_handler(offset, whence):
        input_file.seek(offset, whence)
        return input_file.tell()

    source = pyvips.SourceCustom()
    source.on_read(read_handler)
    source.on_seek(seek_handler)

    return source


def target_custom(filename):
    # w+ means read and write ... we need to be able to read from our output
    # stream for TIFF write
    output_file = open(sys.argv[2], "w+b")

    def write_handler(chunk):
        return output_file.write(chunk)

    # read and seek are optional and only needed for formats like TIFF
    def read_handler(size):
        return output_file.read(size)

    def seek_handler(offset, whence):
        output_file.seek(offset, whence)
        return output_file.tell()

    def end_handler():
        # you can't throw exceptions over on_ handlers, you must return an
        # error code
        try:
            output_file.close()
        except IOError:
            return -1
        else:
            return 0

    target = pyvips.TargetCustom()
    target.on_write(write_handler)
    target.on_read(read_handler)
    target.on_seek(seek_handler)
    target.on_end(end_handler)

    return target


source = source_custom(sys.argv[1])
target = target_custom(sys.argv[2])
image = pyvips.Image.new_from_source(source, '', access='sequential')
image.write_to_target(target, sys.argv[3])
