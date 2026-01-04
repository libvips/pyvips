#!/usr/bin/python

# import logging
# logging.basicConfig(level = logging.DEBUG)

import pyvips

a = pyvips.Image.black(100, 100)
b = a.bandjoin(2)

b.write_to_file("x.v")

txt = pyvips.Image.text("left corner", dpi=300)

c = txt.ifthenelse(2, [0, 255, 0], blend=True)

c.write_to_file("x2.v")
