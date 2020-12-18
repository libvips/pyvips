#!/usr/bin/python3

import sys
import pyvips

source = pyvips.Source.new_from_descriptor(sys.stdin.fileno())
image = pyvips.Image.new_from_source(source, "")
target = pyvips.Target.new_to_descriptor(sys.stdout.fileno())
image.write_to_target(target, ".jpg")
