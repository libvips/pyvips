#!/usr/bin/python3

# import logging
# logging.basicConfig(level = logging.DEBUG)

import pyvips

a = pyvips.Image.black(100, 100)
a = a.draw_circle(128, 50, 50, 20)
b = a.hough_circle(scale=1, min_radius=15, max_radius=25)
b.write_to_file("x.v")
