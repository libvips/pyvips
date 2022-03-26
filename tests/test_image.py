# vim: set fileencoding=utf-8 :

import pyvips
import pytest
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

    def test_bandjoin(self):
        black = pyvips.Image.black(16, 16)
        a = black.draw_rect(1, 0, 0, 1, 1)
        b = black.draw_rect(2, 0, 0, 1, 1)
        c = black.draw_rect(3, 0, 0, 1, 1)
        im = a.bandjoin([b, c, a, b, c, a, b, c])

        assert im.width == 16
        assert im.height == 16
        assert im.bands == 9

        x = im.bandjoin([])
        assert x.bands == 9

    def test_bandslice(self):
        black = pyvips.Image.black(16, 16)
        a = black.draw_rect(1, 0, 0, 1, 1)
        b = black.draw_rect(2, 0, 0, 1, 1)
        c = black.draw_rect(3, 0, 0, 1, 1)
        d = black.draw_rect(4, 0, 0, 1, 1)
        e = black.draw_rect(5, 0, 0, 1, 1)
        f = black.draw_rect(6, 0, 0, 1, 1)

        im = black.bandjoin([a, b, c, d, e, f])

        seq = list(range(im.bands))

        x = im[1]

        assert x.bands == 1
        assert x(0, 0) == [seq[1]]

        x = im[1:4]

        assert x.bands == 3
        assert x(0, 0) == seq[1:4]

        x = im[1:4][::-1]

        assert x.bands == 3
        assert x(0, 0) == seq[1:4][::-1]

        x = im[-7]
        assert x(0, 0) == [seq[-7]]

        x = im[::-1]

        assert x(0, 0) == seq[::-1]

        x = im[4:6]

        assert x(0, 0) == seq[4:6]

        x = im[5:3:-1]

        assert x(0, 0) == seq[5:3:-1]

        x = im[2:4:2]

        assert x(0, 0) == seq[2:4:2]

        c = im[2:0:-2]

        assert x(0, 0) == seq[2:0:-2]

        x = im[::-2]

        assert x(0, 0) == seq[::-2]

        x = im[1::-2]

        assert x(0, 0) == seq[1::-2]

        x = im[:5:-2]

        assert x(0, 0) == seq[:5:-2]

        x = im[5:0:-2]

        assert x(0, 0) == seq[5:0:-2]

        x = im[-10:10]

        assert x(0, 0) == seq[-10:10]

        indices = [1, 2, 5]
        x = im[indices]

        assert x(0, 0) == [seq[i] for i in indices]

        indices = [1, 2, -7]
        x = im[indices]

        assert x(0, 0) == [seq[i] for i in indices]

        indices = [1]
        x = im[indices]

        assert x(0, 0) == [seq[1]]

        indices = [-1]
        x = im[indices]

        assert x(0, 0) == [seq[-1]]

        boolslice = [True, True, False, False, True, True, False]
        x = im[boolslice]
        assert x(0, 0) == [seq[i] for i,b in enumerate(boolslice) if b]

        with pytest.raises(IndexError):
            x = im[4:1]

        with pytest.raises(IndexError):
            x = im[-(im.bands + 1)]

        with pytest.raises(IndexError):
            x = im[im.bands]

        with pytest.raises(IndexError):
            empty = [False] * im.bands
            x = im[empty]

        with pytest.raises(IndexError):
            notenough = [True] * (im.bands - 1)
            x = im[notenough]

        with pytest.raises(IndexError):
            toomany = [True] * (im.bands + 1)
            x = im[toomany]

        with pytest.raises(IndexError):
            empty = []
            x = im[empty]

        with pytest.raises(IndexError):
            oob = [2, 3, -8]
            x = im[oob]

        with pytest.raises(IndexError):
            mixed = [True, 1, True, 2, True, 3, True]
            x = im[mixed]

        with pytest.raises(IndexError):
            wrongtypelist = ['a', 'b', 'c']
            x = im[wrongtypelist]

        with pytest.raises(IndexError):
            wrongargtype = dict(a=1, b=2)
            x = im[wrongargtype]

