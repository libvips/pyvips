# vim: set fileencoding=utf-8 :

import tempfile

import pytest
import pyvips
from helpers import skip_if_no, JPEG_FILE, WEBP_FILE, SVG_FILE


class TestBlock:
    @classmethod
    def setup_class(cls):
        cls.tempdir = tempfile.mkdtemp()

    @skip_if_no('jpegload')
    @skip_if_no('webpload')
    @pytest.mark.skipif(not pyvips.at_least_libvips(8, 13),
                        reason="requires libvips >= 8.13")
    def test_operation_block(self):
        # block all loads except jpeg
        pyvips.operation_block_set("VipsForeignLoad", True)
        pyvips.operation_block_set("VipsForeignLoadJpeg", False)

        image = pyvips.Image.new_from_file(JPEG_FILE)
        assert image.width == 1024

        # should fail
        with pytest.raises(Exception):
            _ = pyvips.Image.new_from_file(WEBP_FILE)

        # reenable all loads
        pyvips.operation_block_set("VipsForeignLoad", False)

    @skip_if_no('jpegload')
    @skip_if_no('svgload')
    @pytest.mark.skipif(not pyvips.at_least_libvips(8, 13),
                        reason="requires libvips >= 8.13")
    def test_block_untrusted(self):
        # block all untrusted operations
        pyvips.block_untrusted_set(True)

        # should fail
        with pytest.raises(Exception):
            _ = pyvips.Image.new_from_file(SVG_FILE)

        # reenable all loads
        pyvips.block_untrusted_set(False)
