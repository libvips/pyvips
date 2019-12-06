# vim: set fileencoding=utf-8 :

import tempfile
import pytest

import pyvips
from helpers import JPEG_FILE, temp_filename, skip_if_no


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
    def test_streamiu_no_seek(self):
        input_file = open(JPEG_FILE, "rb")

        def read_handler(size):
            return input_file.read(size)

        input_stream = pyvips.Streamiu()
        input_stream.on_read(read_handler)

        image = pyvips.Image.new_from_stream(input_stream, '',
                                             access='sequential')
        image2 = pyvips.Image.new_from_file(JPEG_FILE, access='sequential')

        assert abs(image - image2).abs().max() == 0

    @skip_if_no('jpegload')
    @pytest.mark.skipif(not pyvips.at_least_libvips(8, 9),
                        reason="requires libvips >= 8.9")
    def test_streamiu(self):
        input_file = open(JPEG_FILE, "rb")

        def read_handler(size):
            return input_file.read(size)

        def seek_handler(offset, whence):
            input_file.seek(offset, whence)
            return input_file.tell()

        input_stream = pyvips.Streamiu()
        input_stream.on_read(read_handler)
        input_stream.on_seek(seek_handler)

        image = pyvips.Image.new_from_stream(input_stream, '',
                                             access='sequential')
        image2 = pyvips.Image.new_from_file(JPEG_FILE, access='sequential')

        assert abs(image - image2).abs().max() == 0

    @skip_if_no('jpegload')
    @pytest.mark.skipif(not pyvips.at_least_libvips(8, 9),
                        reason="requires libvips >= 8.9")
    def test_streamou(self):
        filename = temp_filename(self.tempdir, '.png')
        output_file = open(filename, "wb")

        def write_handler(chunk):
            return output_file.write(chunk)

        def finish_handler():
            output_file.close()

        output_stream = pyvips.Streamou()
        output_stream.on_write(write_handler)
        output_stream.on_finish(finish_handler)

        image = pyvips.Image.new_from_file(JPEG_FILE, access='sequential')
        image.write_to_stream(output_stream, '.png')

        image2 = pyvips.Image.new_from_file(filename, access='sequential')

        assert abs(image - image2).abs().max() == 0
