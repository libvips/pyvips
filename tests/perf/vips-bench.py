#!/usr/bin/env python3

import pyperf
import pyvips


def vips_bench(loops):
    range_it = range(loops)

    t0 = pyperf.perf_counter()

    for loops in range_it:
        im = pyvips.Image.new_from_file("tmp/x.tif", access='sequential')

        im = im.crop(100, 100, im.width - 200, im.height - 200)
        im = im.reduce(1.0 / 0.9, 1.0 / 0.9, kernel='linear')
        mask = pyvips.Image.new_from_array([[-1, -1, -1],
                                            [-1, 16, -1],
                                            [-1, -1, -1]], scale=8)
        im = im.conv(mask, precision='integer')

        im.write_to_file("tmp/x2.tif")

    return pyperf.perf_counter() - t0


runner = pyperf.Runner()
runner.bench_time_func('vips bench', vips_bench)
