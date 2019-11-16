#!/bin/sh

# Prepare test-images

if [ ! -d tmp ]; then 
	echo building test image ...
	mkdir tmp/
	vips colourspace images/sample2.v tmp/t1.v srgb
	vips replicate tmp/t1.v tmp/t2.v 20 15
	vips extract_area tmp/t2.v tmp/x.tif[tile] 0 0 5000 5000
	vips copy tmp/x.tif tmp/x.jpg
	vipsheader tmp/x.tif
fi

# tune your system to run stable benchmarks ... this needs to run as root
# since it changes some kernel settings
echo please run:
echo "    sudo python3 -m pyperf system tune"
echo to put your system into a stable benchmarking state

# run tests
echo testing vips-bench.py ...
python3 vips-bench.py -o vips-bench.json
python3 -m pyperf stats vips-bench.json

echo testing operation-call.py ...
python3 operation-call.py -o operation-call.json
python3 -m pyperf stats operation-call.json

# command to test if a difference is significant
# python3 -m pyperf compare_to operation-call2.json operation-call.json --table

