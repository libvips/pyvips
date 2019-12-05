#!/usr/bin/env python

from __future__ import print_function

import sys
import pyvips


class Mystreami(pyvips.Streamiu):
    def __init__(self, filename, pipe_mode=False):
        super(Mystreami, self).__init__()

        self.pipe_mode = pipe_mode
        self.loaded_bytes = open(filename, 'rb').read()
        self.memory = memoryview(self.loaded_bytes)
        self.length = len(self.loaded_bytes)
        self.read_point = 0

        self.signal_connect('read', self.read_cb)
        self.signal_connect('seek', self.seek_cb)

    def read_cb(self, buf):
        print('read: {0} bytes ...'.format(len(buf)))
        p = self.read_point
        bytes_available = self.length - p
        bytes_to_copy = min(bytes_available, len(buf))
        buf[:bytes_to_copy] = self.memory[p:p + bytes_to_copy]
        self.read_point += bytes_to_copy
        print('    copied from position {0}'.format(p))

        return bytes_to_copy

    def seek_cb(self, offset, whence):
        print('seek: offset = {0}, whence = {1} ...'
              .format(offset, whence))

        if self.pipe_mode:
            print('   -1 (pipe mode)')
            return -1

        if whence == 0:
            # SEEK_SET
            new_read_point = offset
        elif whence == 1:
            # SEEK_CUR
            new_read_point = self.read_point + offset
        elif whence == 2:
            # SEEK_END
            new_read_point = self.length + offset
        else:
            raise Exception('bad whence {0}'.format(whence))

        self.read_point = max(0, min(self.length, new_read_point))
        print('   new read_point = {0}'.format(self.read_point))

        return self.read_point


class Mystreamo(pyvips.Streamou):
    def __init__(self, filename):
        super(Mystreamo, self).__init__()

        self.f = open(filename, 'wb')

        self.signal_connect('write', self.write_cb)
        self.signal_connect('finish', self.finish_cb)

    def write_cb(self, buf):
        print('write: {0} bytes ...'.format(len(buf)))

        # py2 write does not return number of bytes written
        self.f.write(buf)

        return len(buf)

    def finish_cb(self):
        print('finish: ...')
        self.f.close()


streamiu = Mystreami(sys.argv[1])
image = pyvips.Image.new_from_stream(streamiu, '', access='sequential')

streamou = Mystreamo(sys.argv[2])
image.write_to_stream(streamou, '.png')
