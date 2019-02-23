# vim: set fileencoding=utf-8 :

import os
import tempfile

import pyvips
from helpers import temp_filename, skip_if_no


class TestSaveLoad:
    @classmethod
    def setup_class(cls):
        cls.tempdir = tempfile.mkdtemp()

    @skip_if_no('jpegload')
    def test_save_file(self):
        filename = temp_filename(self.tempdir, '.jpg')

        im = pyvips.Image.black(10, 20)
        im.write_to_file(filename)
        assert os.path.isfile(filename)

        os.remove(filename)

    @skip_if_no('jpegload')
    def test_load_file(self):
        filename = temp_filename(self.tempdir, '.jpg')

        im = pyvips.Image.black(10, 20)
        im.write_to_file(filename)

        x = pyvips.Image.new_from_file(filename)
        assert x.width == 10
        assert x.height == 20
        assert x.bands == 1

        os.remove(x.filename)

    @skip_if_no('jpegload')
    def test_save_buffer(self):
        im = pyvips.Image.black(10, 20)
        buf = im.write_to_buffer('.jpg')
        assert len(buf) > 100

    @skip_if_no('jpegload')
    def test_load_buffer(self):
        im = pyvips.Image.black(10, 20)
        buf = im.write_to_buffer('.jpg')

        x = pyvips.Image.new_from_buffer(buf, '')
        assert x.width == 10
        assert x.height == 20
        assert x.bands == 1
