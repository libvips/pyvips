# vim: set fileencoding=utf-8 :

import os
import pytest

import pyvips


class TestConstants:
    def test_2Darray(self):
        im = pyvips.Image.new_from_array([[1, 2, 3, 4], [5, 6, 7, 8]])
        assert im.width == 4
        assert im.height == 2
