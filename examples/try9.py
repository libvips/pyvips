#!/usr/bin/python3

import logging
import pyvips

logging.basicConfig(level=logging.DEBUG)
a = pyvips.Image.black(100, 100)
a.write_to_file("x.v")
