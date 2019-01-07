#!/usr/bin/python

import logging
logging.basicConfig(level=logging.DEBUG)

import pyvips

a = pyvips.Image.black(100, 100)

a.write_to_file("x.v")
