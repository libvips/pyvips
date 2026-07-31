#!/usr/bin/env python3

import sys
import requests
import pyvips

URL = "https://cdn.filestackcontent.com/bnTGtQw5ShqMPpxH2tMw"
URLS = [URL] * int(sys.argv[1])

session = requests.Session()

image = pyvips.Image.black(1500, 1500)

for i, url in enumerate(URLS):
    print(f"loading {url} ...")
    stream = session.get(url, stream=True).raw

    source = pyvips.SourceCustom()
    source.on_read((lambda stream: stream.read)(stream))

    tile = pyvips.Image.new_from_source(source, "", access="sequential")
    image = image.composite2(tile, "over", x=50 * (i + 1), y=50 * (i + 1))

print("writing output.jpg ...")
image.write_to_file("output.jpg")
