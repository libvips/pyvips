#!/usr/bin/python3

import logging
import pyvips

logging.basicConfig(level=logging.DEBUG)
pyvips.cache_set_trace(True)

try:
    a = pyvips.Image.new_from_file("/home/john/pics/babe.poop")
except pyvips.Error as e:
    print(str(e))

a = pyvips.Image.new_from_file("/home/john/pics/babe.jpg")
b = pyvips.Image.new_from_file("/home/john/pics/k2.jpg")

print('a =', a)
print('b =', b)

out = pyvips.call("add", a, b)

print('out =', out)

out = a.add(b)

print('out =', out)

out = out.linear([1, 1, 1], [2, 2, 2])

out.write_to_file("x.v")
