# vim: set fileencoding=utf-8 :

import tempfile
import pytest

import pyvips
from helpers import JPEG_FILE, temp_filename, skip_if_no

if pyvips.at_least_libvips(8, 9):
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
            p = self.read_point
            bytes_available = self.length - p
            bytes_to_copy = min(bytes_available, len(buf))
            buf[:bytes_to_copy] = self.memory[p:p + bytes_to_copy]
            self.read_point += bytes_to_copy

            return bytes_to_copy

        def seek_cb(self, offset, whence):
            if self.pipe_mode:
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

            return self.read_point

    class Mystreamo(pyvips.Streamou):
        def __init__(self, filename):
            super(Mystreamo, self).__init__()

            self.f = open(filename, 'wb')

            self.signal_connect('write', self.write_cb)
            self.signal_connect('finish', self.finish_cb)

        def write_cb(self, buf):
            # py2 write does not return number of bytes written
            self.f.write(buf)

            return len(buf)

        def finish_cb(self):
            self.f.close()


class TestStreams:
    @classmethod
    def setup_class(cls):
        cls.tempdir = tempfile.mkdtemp()

    @skip_if_no('jpegload')
    @pytest.mark.skipif(not pyvips.at_least_libvips(8, 9),
                        reason="requires libvips >= 8.9")
    def test_stream(self):
        streami = pyvips.Streami.new_from_file(JPEG_FILE)
        image = pyvips.Image.new_from_stream(streami, '', access='sequential')
        filename = temp_filename(self.tempdir, '.png')
        streamo = pyvips.Streamo.new_to_file(filename)
        image.write_to_stream(streamo, '.png')

        image = pyvips.Image.new_from_file(JPEG_FILE, access='sequential')
        image2 = pyvips.Image.new_from_file(filename, access='sequential')

        assert abs(image - image2).abs().max() < 10

    @skip_if_no('jpegload')
    @pytest.mark.skipif(not pyvips.at_least_libvips(8, 9),
                        reason="requires libvips >= 8.9")
    def test_streamu(self):
        streamiu = Mystreami(JPEG_FILE)
        image = pyvips.Image.new_from_stream(streamiu, '', access='sequential')

        filename = temp_filename(self.tempdir, '.jpg')
        streamou = Mystreamo(filename)
        image.write_to_stream(streamou, '.png')

        image = pyvips.Image.new_from_file(JPEG_FILE, access='sequential')
        image2 = pyvips.Image.new_from_file(filename, access='sequential')

        assert abs(image - image2).abs().max() < 10

    @skip_if_no('jpegload')
    @pytest.mark.skipif(not pyvips.at_least_libvips(8, 9),
                        reason="requires libvips >= 8.9")
    def test_streamu_pipe(self):
        streamiu = Mystreami(JPEG_FILE, True)
        image = pyvips.Image.new_from_stream(streamiu, '', access='sequential')

        filename = temp_filename(self.tempdir, '.jpg')
        streamou = Mystreamo(filename)
        image.write_to_stream(streamou, '.png')

        image = pyvips.Image.new_from_file(JPEG_FILE, access='sequential')
        image2 = pyvips.Image.new_from_file(filename, access='sequential')

        assert abs(image - image2).abs().max() < 10
