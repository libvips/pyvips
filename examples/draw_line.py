#!/usr/bin/env python3

# import logging
# logging.basicConfig(level = logging.DEBUG)

import pyvips
from pyvips import ffi


def custom_draw(image, ink, x, y, client):
    assert ffi.from_handle(client) == 42
    print(x, y)


cb = ffi.callback('VipsDrawPoint', custom_draw)
client = ffi.new_handle(42)

im = pyvips.Image.black(100, 100)
im = im.draw_line([100], 0, 0, 100, 0, draw_point=cb, client=client)
