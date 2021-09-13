# vim: set fileencoding=utf-8 :

import pyvips
from helpers import JPEG_FILE


class TestImage:
    def test_pagejoin(self):
        image = pyvips.Image.new_from_file(JPEG_FILE)
        many_page = image.pagejoin([image, image])
        assert many_page.get_page_height() == image.height
        assert many_page.height / many_page.get_page_height() == 3

    def test_pagesplit(self):
        image = pyvips.Image.new_from_file(JPEG_FILE)
        many_page = image.pagejoin([image, image])
        image_list = many_page.pagesplit()
        assert len(image_list) == 3
