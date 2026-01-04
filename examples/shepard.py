#!/usr/bin/python3

# Shepard's distortion, from https://github.com/tourtiere/light-distortion
# with kind permission.

# Use a set of control points to distort an image.
# Usage:
#   ./shepard.py ~/pics/k2.jpg x.jpg "300,400 300,500  300,1500 300,1100"


import re
import sys
from typing import Tuple, List

import pyvips

Point = Tuple[int, int]
Couple = Tuple[Point, Point]


def shepards(image: pyvips.Image, couples: List[Couple]) -> pyvips.Image:
    """Shepard's distortion.

    Distort an image with a set of control points.
    """

    index = pyvips.Image.xyz(image.width, image.height)
    deltas = []
    weights = []
    for p1, p2 in couples:
        diff = index - list(p2)

        distance = (diff[0]**2 + diff[1]**2)
        distance = distance.ifthenelse(distance, 0.1)

        weight = 1.0 / distance

        delta = [(p1[0] - p2[0]), (p1[1] - p2[1])] * weight

        weights.append(weight)
        deltas.append(delta)

    # add, normalize
    index += pyvips.Image.sum(deltas) / pyvips.Image.sum(weights)

    return image.mapim(index, interpolate=pyvips.Interpolate.new('bicubic'))


if __name__ == '__main__':
    image = pyvips.Image.new_from_file(sys.argv[1])
    matches = re.findall(r'(\d+),(\d+) (\d+),(\d+)', sys.argv[3])
    couples = [((int(m[0]), int(m[1])), (int(m[2]), int(m[3])))
               for m in matches]

    image = shepards(image, couples)

    image.write_to_file(sys.argv[2])
