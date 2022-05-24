# vim: set fileencoding=utf-8 :

import tempfile
import pytest

import pyvips
from helpers import JPEG_FILE, WEBP_FILE, temp_filename, skip_if_no


class TestConnections:
    @classmethod
    def setup_class(cls):
        cls.tempdir = tempfile.mkdtemp()

    @skip_if_no('jpegload')
    @pytest.mark.skipif(not pyvips.at_least_libvips(8, 9),
                        reason="requires libvips >= 8.9")
    def test_connection(self):
        source = pyvips.Source.new_from_file(JPEG_FILE)
        image = pyvips.Image.new_from_source(source, '', access='sequential')
        filename = temp_filename(self.tempdir, '.png')
        target = pyvips.Target.new_to_file(filename)
        image.write_to_target(target, '.png')

        image = pyvips.Image.new_from_file(JPEG_FILE, access='sequential')
        image2 = pyvips.Image.new_from_file(filename, access='sequential')

        assert (image - image2).abs().max() < 10

    @skip_if_no('jpegload')
    @pytest.mark.skipif(not pyvips.at_least_libvips(8, 9),
                        reason="requires libvips >= 8.9")
    def test_source_custom_no_seek(self):
        input_file = open(JPEG_FILE, "rb")

        def read_handler(size):
            return input_file.read(size)

        source = pyvips.SourceCustom()
        source.on_read(read_handler)

        image = pyvips.Image.new_from_source(source, '', access='sequential')
        image2 = pyvips.Image.new_from_file(JPEG_FILE, access='sequential')

        assert (image - image2).abs().max() == 0

    @skip_if_no('jpegload')
    @pytest.mark.skipif(not pyvips.at_least_libvips(8, 9),
                        reason="requires libvips >= 8.9")
    def test_source_custom(self):
        input_file = open(JPEG_FILE, "rb")

        def read_handler(size):
            return input_file.read(size)

        def seek_handler(offset, whence):
            input_file.seek(offset, whence)
            return input_file.tell()

        source = pyvips.SourceCustom()
        source.on_read(read_handler)
        source.on_seek(seek_handler)

        image = pyvips.Image.new_from_source(source, '',
                                             access='sequential')
        image2 = pyvips.Image.new_from_file(JPEG_FILE, access='sequential')

        assert (image - image2).abs().max() == 0

    @skip_if_no('jpegload')
    @pytest.mark.skipif(not pyvips.at_least_libvips(8, 9),
                        reason="requires libvips >= 8.9")
    def test_target_custom(self):
        filename = temp_filename(self.tempdir, '.png')
        output_file = open(filename, "w+b")

        def write_handler(chunk):
            return output_file.write(chunk)

        def end_handler():
            try:
                output_file.close()
            except IOError:
                return -1
            else:
                return 0

        target = pyvips.TargetCustom()
        target.on_write(write_handler)
        target.on_end(end_handler)

        image = pyvips.Image.new_from_file(JPEG_FILE, access='sequential')
        image.write_to_target(target, '.png')

        image = pyvips.Image.new_from_file(JPEG_FILE, access='sequential')
        image2 = pyvips.Image.new_from_file(filename, access='sequential')

        assert (image - image2).abs().max() == 0

    @skip_if_no('jpegload')
    @skip_if_no('tiffsave')
    @pytest.mark.skipif(not pyvips.at_least_libvips(8, 13),
                        reason="requires libvips >= 8.13")
    def test_target_custom_seek(self):
        filename = temp_filename(self.tempdir, '.png')
        output_file = open(filename, "w+b")

        def write_handler(chunk):
            return output_file.write(chunk)

        def read_handler(size):
            return output_file.read(size)

        def seek_handler(offset, whence):
            output_file.seek(offset, whence)
            return output_file.tell()

        def end_handler():
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

        image = pyvips.Image.new_from_file(JPEG_FILE, access='sequential')
        image.write_to_target(target, '.tif')

        image = pyvips.Image.new_from_file(JPEG_FILE, access='sequential')
        image2 = pyvips.Image.new_from_file(filename, access='sequential')

        assert (image - image2).abs().max() == 0

    # test webp as well, since that maps the stream rather than using read

    @skip_if_no('webpload')
    @pytest.mark.skipif(not pyvips.at_least_libvips(8, 9),
                        reason="requires libvips >= 8.9")
    def test_source_custom_webp_no_seek(self):
        input_file = open(WEBP_FILE, "rb")

        def read_handler(size):
            return input_file.read(size)

        source = pyvips.SourceCustom()
        source.on_read(read_handler)

        image = pyvips.Image.new_from_source(source, '',
                                             access='sequential')
        image2 = pyvips.Image.new_from_file(WEBP_FILE, access='sequential')

        assert (image - image2).abs().max() == 0

    @skip_if_no('webpload')
    @pytest.mark.skipif(not pyvips.at_least_libvips(8, 9),
                        reason="requires libvips >= 8.9")
    def test_source_custom_webp(self):
        input_file = open(WEBP_FILE, "rb")

        def read_handler(size):
            return input_file.read(size)

        def seek_handler(offset, whence):
            input_file.seek(offset, whence)
            return input_file.tell()

        source = pyvips.SourceCustom()
        source.on_read(read_handler)
        source.on_seek(seek_handler)

        image = pyvips.Image.new_from_source(source, '',
                                             access='sequential')
        image2 = pyvips.Image.new_from_file(WEBP_FILE, access='sequential')

        assert (image - image2).abs().max() == 0
