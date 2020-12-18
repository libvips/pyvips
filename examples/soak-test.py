#!/usr/bin/python3

import sys
import pyvips

pyvips.leak_set(True)
pyvips.cache_set_max(0)

for i in range(1000):
    print("loop {0} ...".format(i))
    im = pyvips.Image.new_from_file(sys.argv[1])
    im = im.embed(100, 100, 3000, 3000, extend="mirror")
    im.write_to_file("x.v")
