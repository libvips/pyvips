#!/usr/bin/python3

import sys
import pyvips

x = pyvips.Image.new_from_file(sys.argv[1])
if not x.hasalpha():
    x = x.addalpha()
y = x.affine([0.70710678, 0.70710678, -0.70710678, 0.70710678])
y.write_to_file(sys.argv[2])
